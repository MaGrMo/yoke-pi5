# yoke-pi5

Yocto (scarthgap) + ROS 2 Jazzy firmware for Raspberry Pi 5.

## What the image provides
- ROS 2 Jazzy (`ros-core`) in `/opt/ros/jazzy`
- WiFi that connects automatically on boot (sysvinit + ifupdown + wpa_supplicant)
- User `yoke` with a password, SSH key login and `sudo` (password required); root is locked
- Dropbear SSH server; works with VS Code Remote-SSH
- 4 GiB of free space on the root partition
- GPS tracker with phone notifications (ROS 2 nodes started on boot), see [GPS tracker](#gps-tracker)

## Layout
- `layers/` — layers as git submodules + our own `meta-yoke` layer
- `layers/meta-yoke/conf/templates/default/` — local.conf and bblayers.conf
- `layers/meta-yoke/recipes-core/images/yoke-image.bb` — image recipe
- `layers/meta-yoke/recipes-core/yoke-user/` — user `yoke`, SSH key, sudoers
- `layers/meta-yoke/recipes-connectivity/wpa-supplicant/` — WiFi network config
- `build.sh` — build on the current machine
- `docker-build.sh` — build in an Ubuntu 22.04 container (this is how CI works)

## Building
The image is built by CI (self-hosted runner) on every push to `main`. Download
`yoke-pi5-<sha>` from the workflow run's artifacts.

Local build, if needed:

    git clone --recursive git@github.com:MaGrMo/yoke-pi5.git
    ./docker-build.sh          # recommended
    ./build.sh                 # directly on a Linux host

Resulting image: `build/tmp/deploy/images/raspberrypi5/yoke-image-raspberrypi5.rootfs.wic.bz2`

## CI secrets
Set in GitHub → Settings → Secrets and variables → Actions → Secrets:
- `WIFI_SSID`, `WIFI_PSK` — WiFi network the Pi connects to on boot
- `YOKE_PASSWORD_HASH` — password hash for user `yoke` (`openssl passwd -6`; on macOS use Homebrew's openssl)
- `NTFY_TOPIC` — ntfy topic for the GPS notifications (see [GPS tracker](#gps-tracker))

## Writing to an SD card
    sudo bmaptool copy yoke-image-raspberrypi5.rootfs.wic.bz2 /dev/sdX   # needs the .bmap next to it

or, on macOS without bmaptool (slower, writes the empty space too):

    bzcat yoke-image-raspberrypi5.rootfs.wic.bz2 | sudo dd of=/dev/rdiskN bs=4m

## Connecting
    ssh-keygen -R <pi-ip>      # after every reflash: the SSH host key changes
    ssh -i ~/.ssh/id_ed25519_raspi yoke@<pi-ip>

## Changing settings
Edit the template in `meta-yoke`, then `rm -rf build/conf` and rerun the build
(CI starts from a clean `build/` every time).

## GPS tracker
A u-blox NEO-6M GPS on the Pi's UART; the Pi sends a phone notification when it moves.
ROS packages are in `ros/` (`yoke_interfaces`, `yoke_location`), their recipes in `layers/meta-yoke/recipes-ros/`.

    NEO-6M ──UART──▶ [gps_node] ──/fix──▶ [location_monitor] ──/notify──▶ [notifier] ──HTTP──▶ ntfy.sh ──▶ phone

### Nodes
- **`gps_node`** — reads NMEA `GGA` sentences from `/dev/ttyAMA0` at 9600 baud (pyserial),
  publishes `sensor_msgs/NavSatFix` on `/fix`. (The stock `nmea_navsat_driver` is not used: its
  `tf-transformations` dependency has an unresolved `python3-transforms3d` in meta-ros.)
- **`location_monitor`** — subscribes to `/fix`, ignores samples without a fix, and calls `/notify`:
  - on the first GPS fix (this becomes the reference point);
  - when the position is more than 100 m from the last notified point for 3 samples in a row
    (filters out GPS jumps); the new position becomes the reference point.
- **`notifier`** — provides the `/notify` service and sends notifications through
  [ntfy](https://ntfy.sh) (no account or password). On startup it sends "Yoke online" with the Pi's IP, retrying until the network is up.

### Interface
`yoke_interfaces/srv/Notify`:

    string title
    string message
    ---
    bool success
    string error

The service replies after ntfy confirmed delivery or all retries failed. Manual test:

    ros2 service call /notify yoke_interfaces/srv/Notify "{title: test, message: hello}"

### System changes
- Kernel console moves from `ttyAMA0` (GPIO14/15) to the Pi 5 debug UART `ttyAMA10`, freeing the GPIO UART for GPS.
- User `yoke` joins group `dialout` to read `/dev/ttyAMA0`.
- `chrony` for NTP time sync (the Pi has no battery-backed clock).
- ROS starts on boot from `/etc/init.d/yoke-ros` (log: `/var/log/yoke-ros.log`); nodes respawn if they crash.
  `sudo /etc/init.d/yoke-ros restart|stop|status`. `/etc/profile.d/ros.sh` sources ROS in every login shell.
- CI secret `NTFY_TOPIC` — a long random ntfy topic name (letters, digits, `-`, `_`); anyone who knows it can
  read the notifications. Subscribe to the same topic in the ntfy phone app. Generate and store it with:

      T="yoke-$(openssl rand -hex 12)"; echo $T; gh secret set NTFY_TOPIC --body "$T"

### Wiring
| NEO-6M | Pi 5 |
|---|---|
| VCC | pin 1 (3.3 V) or pin 2 (5 V) |
| GND | pin 6 |
| TX  | pin 10 (GPIO15, RXD) |
| RX  | pin 8 (GPIO14, TXD) |
