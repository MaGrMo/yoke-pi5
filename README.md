# yoke-pi5

Yocto (scarthgap) + ROS 2 Jazzy для Raspberry Pi 5.

## Структура
- `layers/` — шари як git submodules + власний шар `meta-yoke`
- `layers/meta-yoke/conf/templates/default/` — local.conf і bblayers.conf
- `layers/meta-yoke/recipes-core/images/yoke-image.bb` — рецепт образу
- `build.sh` — збірка на поточній машині
- `docker-build.sh` — збірка в контейнері Ubuntu 22.04 (так працює CI)

## Перший запуск (один раз)
    ./scripts/setup-submodules.sh
    git add . && git commit -m "Add layers" && git push

## Клонування
    git clone --recursive git@github.com:MaGrMo/yoke-pi5.git

## Локальна збірка
    ./docker-build.sh          # рекомендовано
    ./build.sh                 # напряму на хості

Готовий образ: `build/tmp/deploy/images/raspberrypi5/yoke-image-raspberrypi5.rootfs.wic.bz2`

## Запис на SD-карту
    sudo bmaptool copy yoke-image-raspberrypi5.rootfs.wic.bz2 /dev/sdX

## Зміна налаштувань
Правте шаблон у `meta-yoke`, потім `rm -rf build/conf` і перезапустіть збірку.
