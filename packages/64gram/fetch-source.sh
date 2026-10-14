#!/usr/bin/bash
# Fetch the official 64Gram Linux build plus the desktop/metainfo/icon files from the same tag.
# Usage: fetch-source.sh <version> <destdir>
set -euo pipefail
version=$1; dest=$2
repo=https://github.com/TDesktop-x64/tdesktop
raw=https://raw.githubusercontent.com/TDesktop-x64/tdesktop/v$version
asset=64Gram_${version}_linux.zip
zip=$dest/64gram-$version-linux.zip

curl -fsSL --retry 3 -o "$zip" "$repo/releases/download/v$version/$asset"

# Expected digest from GitHub's release page (no API, so no rate limit).
want=$(curl -fsSL --retry 3 "$repo/releases/expanded_assets/v$version" | tr -d '\n' |
       grep -oE "$asset.{0,600}" | grep -oE 'sha256:[0-9a-f]{64}' | head -1 | cut -d: -f2)
[[ -n $want ]] || { echo "could not find a published sha256 for $asset" >&2; exit 1; }
echo "$want  $zip" | sha256sum -c -

for f in LICENSE LEGAL \
         lib/xdg/io.github.tdesktop_x64.TDesktop.desktop \
         lib/xdg/io.github.tdesktop_x64.TDesktop.metainfo.xml \
         lib/xdg/io.github.tdesktop_x64.TDesktop.service; do
  curl -fsSL --retry 3 -o "$dest/$(basename "$f")" "$raw/$f"
done
for size in 16 32 48 64 128 256 512; do
  curl -fsSL --retry 3 -o "$dest/icon$size.png" "$raw/Telegram/Resources/art/icon$size.png"
done
