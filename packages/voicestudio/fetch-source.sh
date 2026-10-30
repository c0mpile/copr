#!/usr/bin/bash
# Fetch the official release .deb and verify it against the release's SHA256SUMS.txt.
# Usage: fetch-source.sh <version> <destdir>
set -euo pipefail
version=$1; dest=$2
base=https://github.com/debpalash/VoiceStudio/releases/download/v$version
deb=VoiceStudio-Electron-$version-linux-x64.deb

curl -fsSL --retry 3 -o "$dest/SHA256SUMS.txt" "$base/SHA256SUMS.txt"
curl -fsSL --retry 3 -o "$dest/voicestudio-electron-$version-linux-x64.deb" "$base/$deb"
want=$(grep -F " $deb" "$dest/SHA256SUMS.txt" | cut -d' ' -f1)
[[ -n $want ]] || { echo "no checksum for $deb in SHA256SUMS.txt" >&2; exit 1; }
echo "$want  $dest/voicestudio-electron-$version-linux-x64.deb" | sha256sum -c -
rm -f "$dest/SHA256SUMS.txt"
