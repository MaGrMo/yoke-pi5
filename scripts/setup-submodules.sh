#!/usr/bin/env bash
# Одноразово: додає всі шари як git submodules (запускати з кореня репозиторію)
set -euo pipefail
cd "$(dirname "$0")/.."

git submodule add -b scarthgap        https://git.yoctoproject.org/poky                     layers/poky
git submodule add -b scarthgap        https://git.yoctoproject.org/meta-raspberrypi         layers/meta-raspberrypi
git submodule add -b scarthgap/u-boot https://git.yoctoproject.org/meta-lts-mixins          layers/meta-lts-mixins
git submodule add -b scarthgap        https://git.openembedded.org/meta-openembedded        layers/meta-openembedded
git submodule add -b scarthgap        https://git.yoctoproject.org/meta-virtualization      layers/meta-virtualization
git submodule add -b scarthgap        https://github.com/ros/meta-ros.git                   layers/meta-ros

echo "Готово. Тепер: git add . && git commit -m 'Add layers' && git push"
