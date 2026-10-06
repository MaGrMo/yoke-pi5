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

# GPS tracker: ROS nodes started on boot, NTP for correct time (TLS needs it)
IMAGE_INSTALL:append = " \
    yoke-ros \
    chrony \
    chronyc \
"

# Needed by the VS Code Remote-SSH server
IMAGE_INSTALL:append = " \
    bash \
    ldd \
    glibc-utils \
    os-release \
"

# The root partition grows to the whole SD card on first boot (yoke-growfs).
# Until then keep 512 MiB free (in KB), enough for the VS Code server.
IMAGE_INSTALL:append = " yoke-growfs"
IMAGE_ROOTFS_EXTRA_SPACE = "524288"
