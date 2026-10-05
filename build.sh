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

bitbake "$IMAGE" "$@"
