#!/usr/bin/env bash
# Запускає build.sh у контейнері Ubuntu 22.04 (офіційно підтримуваний хост для scarthgap)
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
  yoke-builder ./build.sh "$@"
