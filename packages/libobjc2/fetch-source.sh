#!/usr/bin/bash
# Fetch the upstream release tarball. Usage: fetch-source.sh <version> <destdir>
set -euo pipefail
curl -fsSL --retry 3 -o "$2/libobjc2-$1.tar.gz" "https://github.com/gnustep/libobjc2/archive/refs/tags/v$1.tar.gz"
