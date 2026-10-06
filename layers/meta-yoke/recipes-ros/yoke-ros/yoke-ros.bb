SUMMARY = "Starts the Yoke ROS 2 nodes on boot and sets up the ROS shell environment"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://yoke-ros.init \
    file://ros.sh \
"
S = "${WORKDIR}"

inherit update-rc.d useradd

INITSCRIPT_NAME = "yoke-ros"
# Start last, after networking
INITSCRIPT_PARAMS = "start 99 2 3 4 5 . stop 10 0 1 6 ."

# User yoke (from yoke-user) needs the serial port for the GPS
USERADD_PACKAGES = "${PN}"
USERADD_DEPENDS = "yoke-user"
GROUPMEMS_PARAM:${PN} = "-a yoke -g dialout"

# ntfy topic from build.sh via site.conf; anyone who knows it can read the notifications
NTFY_TOPIC ??= ""

python () {
    import re
    topic = d.getVar('NTFY_TOPIC')
    if topic and not re.fullmatch(r'[-_A-Za-z0-9]{1,64}', topic):
        bb.fatal('NTFY_TOPIC may only contain letters, digits, "-" and "_" (max 64)')
}

do_install() {
    install -D -m 0755 ${S}/yoke-ros.init ${D}${sysconfdir}/init.d/yoke-ros
    install -D -m 0644 ${S}/ros.sh ${D}${sysconfdir}/profile.d/ros.sh

    install -d -m 0755 ${D}${sysconfdir}/yoke
    echo "topic=${NTFY_TOPIC}" > ${D}${sysconfdir}/yoke/ntfy.conf
    chown yoke:yoke ${D}${sysconfdir}/yoke/ntfy.conf
    chmod 0600 ${D}${sysconfdir}/yoke/ntfy.conf
}

CONFFILES:${PN} = "${sysconfdir}/yoke/ntfy.conf"
RDEPENDS:${PN} = "yoke-location yoke-user"
