SUMMARY = "Yoke login user: password, SSH key and sudo"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = " \
    file://authorized_keys \
    file://sudoers-wheel \
"
S = "${WORKDIR}"

inherit useradd

YOKE_USER ??= "yoke"
# Hash from `openssl passwd -6`, with $ escaped as \$ (build.sh does this).
# Without a hash the password is locked and only SSH key login works.
YOKE_PASSWORD_HASH ??= ""

YOKE_PASSWORD_OPT = ""
python __anonymous() {
    pw = d.getVar('YOKE_PASSWORD_HASH')
    if pw:
        d.setVar('YOKE_PASSWORD_OPT', "-p '%s'" % pw)
}

USERADD_PACKAGES = "${PN}"
GROUPADD_PARAM:${PN} = "${YOKE_USER}"
USERADD_PARAM:${PN} = "-d /home/${YOKE_USER} -s /bin/sh -g ${YOKE_USER} -G wheel ${YOKE_PASSWORD_OPT} ${YOKE_USER}"

do_install() {
    install -d -m 0755 -o ${YOKE_USER} -g ${YOKE_USER} ${D}/home/${YOKE_USER}
    install -d -m 0700 -o ${YOKE_USER} -g ${YOKE_USER} ${D}/home/${YOKE_USER}/.ssh
    install -m 0600 -o ${YOKE_USER} -g ${YOKE_USER} ${S}/authorized_keys ${D}/home/${YOKE_USER}/.ssh/authorized_keys

    install -d -m 0750 ${D}${sysconfdir}/sudoers.d
    install -m 0440 ${S}/sudoers-wheel ${D}${sysconfdir}/sudoers.d/wheel
}

FILES:${PN} = "/home/${YOKE_USER} ${sysconfdir}/sudoers.d"
RDEPENDS:${PN} = "sudo"
