SUMMARY = "Grows the root partition to the whole SD card on first boot"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

SRC_URI = "file://yoke-growfs.init"
S = "${WORKDIR}"

inherit update-rc.d

INITSCRIPT_NAME = "yoke-growfs"
# Early in the boot, right after the local filesystems are mounted
INITSCRIPT_PARAMS = "start 05 2 3 4 5 ."

do_install() {
    install -D -m 0755 ${S}/yoke-growfs.init ${D}${sysconfdir}/init.d/yoke-growfs
}

RDEPENDS:${PN} = " \
    util-linux-sfdisk \
    util-linux-partx \
    e2fsprogs-resize2fs \
"
