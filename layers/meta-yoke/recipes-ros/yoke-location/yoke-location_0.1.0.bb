SUMMARY = "Yoke GPS reader, location monitor and ntfy notifier (ROS 2)"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COMMON_LICENSE_DIR}/MIT;md5=0835ade698e0bcf8506ecda2f7b4f302"

# Source lives in the repo's ros/ directory, not in the layer
FILESEXTRAPATHS:prepend := "${THISDIR}/../../../../ros:"
SRC_URI = "file://yoke_location"
S = "${WORKDIR}/yoke_location"

inherit ros_distro_jazzy ros_component

RDEPENDS:${PN} += " \
    rclpy \
    sensor-msgs \
    yoke-interfaces \
    python3-pyserial \
    launch \
    launch-ros \
    ros2launch \
"

ROS_BUILD_TYPE = "ament_python"
inherit ros_${ROS_BUILD_TYPE}
