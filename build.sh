#!/usr/bin/env bash
# Збирає образ. Працює і на хості, і всередині Docker-контейнера.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

IMAGE="${IMAGE:-yoke-image}"
export MACHINE="${MACHINE:-raspberrypi5}"

# Кеші поза build/, щоб переживали очищення робочої директорії
CACHE="${YOKE_CACHE:-$ROOT/cache}"
export DL_DIR="$CACHE/downloads"
export SSTATE_DIR="$CACHE/sstate-cache"
mkdir -p "$DL_DIR" "$SSTATE_DIR"

git submodule update --init --recursive

# Конфіг береться з нашого шару, а не з meta-poky
export TEMPLATECONF="$ROOT/layers/meta-yoke/conf/templates/default"
set +u
source layers/poky/oe-init-build-env "$ROOT/build" > /dev/null
set -u

cat > conf/site.conf <<EOF
DL_DIR = "$DL_DIR"
SSTATE_DIR = "$SSTATE_DIR"
EOF

# Хеш пароля користувача yoke (openssl passwd -6); $ екрануємо для useradd
if [ -n "${YOKE_PASSWORD_HASH:-}" ]; then
  echo "YOKE_PASSWORD_HASH = \"${YOKE_PASSWORD_HASH//\$/\\\$}\"" >> conf/site.conf
fi

# WiFi для автопідключення (див. meta-yoke wpa-supplicant bbappend)
if [ -n "${WIFI_SSID:-}" ]; then
  cat >> conf/site.conf <<EOF
WIFI_SSID = "$WIFI_SSID"
WIFI_PSK = "${WIFI_PSK:-}"
EOF
  if [ -n "${WIFI_COUNTRY:-}" ]; then
    echo "WIFI_COUNTRY = \"$WIFI_COUNTRY\"" >> conf/site.conf
  fi
fi

bitbake "$IMAGE" "$@"
