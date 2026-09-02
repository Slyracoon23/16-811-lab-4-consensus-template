#!/usr/bin/env bash
# Ubuntu 24.04's Python is externally managed and apt owns several of the packages this project
# depends on. pip cannot uninstall an apt-installed distribution — it fails with "RECORD file not
# found" — so apt provides the dependencies and pip only registers the project itself with
# --no-deps. Installing them the other way round is what broke the first build here.
set -euo pipefail

apt-get update
apt-get install -y --no-install-recommends python3-pip python3-pytest python3-numpy

# The bridge is what Foxglove connects through. Nice to have, never required: the fleet runs and
# CI checks it without any viewer attached, so a missing package must not fail the build.
apt-get install -y --no-install-recommends ros-jazzy-foxglove-bridge \
  || echo "foxglove_bridge unavailable in this image; the fleet still runs, you just cannot watch it"

rm -rf /var/lib/apt/lists/*
pip install --break-system-packages --no-deps -e .
