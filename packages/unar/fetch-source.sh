#!/usr/bin/bash
# Fetch XADMaster (the unar/lsar sources) and its UniversalDetector dependency.
# Usage: fetch-source.sh <version> <destdir>
set -euo pipefail
detector=1.1
curl -fsSL --retry 3 -o "$2/unar-$1.tar.gz" "https://github.com/MacPaw/XADMaster/archive/v$1/unar-$1.tar.gz"
curl -fsSL --retry 3 -o "$2/universal-detector-$detector.tar.gz" \
  "https://github.com/MacPaw/universal-detector/archive/$detector/universal-detector-$detector.tar.gz"
