#!/usr/bin/bash
# Print packages/<pkg>/copr_script.sh with its commit placeholders filled in.
# Usage: render-copr-script.sh <pkg> <fedora-dist-git-commit> <packaging-clone-url> [packaging-commit]
set -euo pipefail
cd "$(dirname "$0")/.."
pkg=$1; fedora=$2; url=$3; commit=${4:-$(git rev-parse HEAD)}
sed -e "s|@FEDORA_COMMIT@|$fedora|" -e "s|@PACKAGING_URL@|$url|" -e "s|@PACKAGING_COMMIT@|$commit|" \
  "packages/$pkg/copr_script.sh"
