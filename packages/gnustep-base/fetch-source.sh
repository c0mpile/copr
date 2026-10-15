#!/usr/bin/bash
# Fetch the upstream release tarball. Usage: fetch-source.sh <version> <destdir>
set -euo pipefail
curl -fsSL --retry 3 -o "$2/gnustep-base-$1.tar.gz" "https://ftp.gnustep.org/pub/gnustep/core/gnustep-base-$1.tar.gz"
