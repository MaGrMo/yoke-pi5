#!/usr/bin/env bash
# Runs build.sh in an Ubuntu 22.04 container (officially supported host for scarthgap)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE="${YOKE_CACHE:-$ROOT/cache}"
mkdir -p "$CACHE"

docker build -t yoke-builder \
  --build-arg UID="$(id -u)" --build-arg GID="$(id -g)" \
  "$ROOT/docker"

TTY=""
[ -t 1 ] && TTY="-it"

docker run --rm $TTY \
  -v "$ROOT:$ROOT" -v "$CACHE:$CACHE" -w "$ROOT" \
  -e YOKE_CACHE="$CACHE" -e MACHINE -e IMAGE \
  -e WIFI_SSID -e WIFI_PSK -e WIFI_COUNTRY -e YOKE_PASSWORD_HASH -e NTFY_TOPIC \
  yoke-builder ./build.sh "$@"
