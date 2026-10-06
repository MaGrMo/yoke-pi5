SUMMARY = "Yoke ROS 2 message and service definitions"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

# Source lives in the repo's ros/ directory, not in the layer
FILESEXTRAPATHS:prepend := "${THISDIR}/../../../../ros:"
SRC_URI = "file://yoke_interfaces"
S = "${WORKDIR}/yoke_interfaces"

inherit ros_distro_jazzy ros_component

DEPENDS = " \
    ament-cmake-native \
    rosidl-default-generators-native \
"
# Without the target dependencies ament finds the native (x86) libraries and fails to link
# ("file in wrong format"); same fix as meta-ros applies to std-srvs
DEPENDS += " \
    rosidl-default-runtime \
    service-msgs \
"
RDEPENDS:${PN} += " \
    rosidl-default-runtime \
    builtin-interfaces \
"

ROS_BUILD_TYPE = "ament_cmake"
inherit ros_${ROS_BUILD_TYPE}
