#!/bin/sh
# Reproduces this example in a container: builds LeanDrift's image, then builds, exports and
# compares the project at the two commits. The report lands in out/ beside this script.
set -e
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
docker build -q -t leandrift -f "$root/docker/Dockerfile" "$root" >/dev/null
mkdir -p "$here/out"
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -v leandrift-elan:/opt/elan -v leandrift-cache:/cache -v "$here/out:/out" \
  leandrift leandrift compare https://github.com/YaelDillies/misc-yd a7b57745ba06180ae7b1e6ef43489e035c21600d^ a7b57745ba06180ae7b1e6ef43489e035c21600d --prefix MiscYD --workdir /tmp/work --out /out
