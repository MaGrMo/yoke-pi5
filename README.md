# yoke-pi5

Yocto (scarthgap) + ROS 2 Jazzy for Raspberry Pi 5.

## Layout
- `layers/` — layers as git submodules + our own `meta-yoke` layer
- `layers/meta-yoke/conf/templates/default/` — local.conf and bblayers.conf
- `layers/meta-yoke/recipes-core/images/yoke-image.bb` — image recipe
- `build.sh` — build on the current machine
- `docker-build.sh` — build in an Ubuntu 22.04 container (this is how CI works)

## First run (once)
    ./scripts/setup-submodules.sh
    git add . && git commit -m "Add layers" && git push

## Cloning
    git clone --recursive git@github.com:MaGrMo/yoke-pi5.git

## Local build
    ./docker-build.sh          # recommended
    ./build.sh                 # directly on the host

Resulting image: `build/tmp/deploy/images/raspberrypi5/yoke-image-raspberrypi5.rootfs.wic.bz2`

## CI secrets
Set in GitHub → Settings → Secrets and variables → Actions → Secrets:
- `WIFI_SSID`, `WIFI_PSK` — WiFi network the Pi connects to on boot
- `YOKE_PASSWORD_HASH` — password hash for user `yoke` (`openssl passwd -6`; on macOS use Homebrew's openssl)

## Writing to an SD card
    sudo bmaptool copy yoke-image-raspberrypi5.rootfs.wic.bz2 /dev/sdX

## Changing settings
Edit the template in `meta-yoke`, then `rm -rf build/conf` and rerun the build.
