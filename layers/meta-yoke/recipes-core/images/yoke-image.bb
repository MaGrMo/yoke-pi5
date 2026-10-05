SUMMARY = "Yoke firmware: Raspberry Pi 5 + ROS 2 Jazzy"
LICENSE = "MIT"

inherit core-image

IMAGE_FEATURES += "ssh-server-dropbear"

IMAGE_INSTALL:append = " \
    ros-core \
    nano \
    curl \
    wpa-supplicant \
    iw \
    yoke-user \
"
