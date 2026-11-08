#!/bin/sh
# Reproduces this example in a container: builds LeanDrift's image, then builds, exports and
# compares the project at the two commits. The report lands in out/ beside this script.
set -e
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
echo "building the leandrift image..."
docker build -q -t leandrift -f "$root/docker/Dockerfile" "$root" >/dev/null
echo "comparing (the first run downloads two toolchains and Mathlib's cache)..."
mkdir -p "$here/out"
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
  -v leandrift-elan:/opt/elan -v leandrift-cache:/cache -v "$here/out:/out" \
  leandrift leandrift compare https://github.com/YaelDillies/cam-combi 34a573b79a64c9521e9e85e5ea1e58e276e7cebc^ 34a573b79a64c9521e9e85e5ea1e58e276e7cebc --prefix LeanCamCombi --workdir /tmp/work --out /out \
  --title "LeanDrift report: cam-combi 34a573b^ -> 34a573b"
