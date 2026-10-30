#!/usr/bin/bash
# Dry-run a package's spec patches against Fedora's dist-git files, so a drifted patch is caught before a
# Copr build is submitted (and before an autofix PR is opened).
# Usage: check-patches.sh <pkg> <dist-git-url> <branch> <commit> <save-dir>   fetch the commit; on failure
#                                                                            save the files the patches touch
#        check-patches.sh <pkg> --local <dir>                                check against such a saved dir
# Exit: 0 patches apply; 1 they don't (rejects on stdout); 3 could not fetch the commit (unchecked; the build
#       is submitted anyway and would fail in the SRPM stage).
# Patches are applied with fuzz 0, like rpmbuild does.
# use-system-python.patch applies to the Chromium source tree, of which only .gn is fetched (from Chromium's
# git, at the spec's Version) and checked.
set -euo pipefail
pkg=$1; shift
root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
patches=(modify.patch rename.patch use-system-python.patch)

if [[ $1 == --local ]]; then
  cp -a "$2" "$work/src"
  cd "$work/src"
else
  url=$1; branch=$2; commit=$3; save=$4
  git clone -q --depth 1 --branch "$branch" "$url" "$work/src" 2>/dev/null || exit 3
  cd "$work/src"
  if [[ $(git rev-parse HEAD) != "$commit" ]]; then
    git fetch -q --depth 1 origin "$commit" 2>/dev/null && git checkout -q FETCH_HEAD || exit 3
  fi
  # Keep the files the patches touch (small), for whoever has to fix them without network.
  rm -rf "$save"; mkdir -p "$save"
  for p in "${patches[@]}"; do sed -nE 's|^diff --git a/(\S+) b/.*|\1|p' "$root/packages/$pkg/$p"; done | sort -u |
    while read -r f; do [[ ! -f $f ]] || cp "$f" "$save/"; done
  ver=$(sed -nE 's/^Version:[[:space:]]*([0-9.]+).*/\1/p' chromium.spec | head -1)
  curl -fsS --retry 3 "https://chromium.googlesource.com/chromium/src/+/refs/tags/$ver/.gn?format=TEXT" |
    base64 -d > "$save/.gn" || { rm -rf "$save"; exit 3; }
  cp "$save/.gn" .gn
fi

# The patches may be agent-written (autofix): refuse absolute or parent-relative paths and symlinks outright.
for p in "${patches[@]}"; do
  if sed -E 's|/dev/null||g' "$root/packages/$pkg/$p" |
     grep -qE '^(\+\+\+|---|diff --git|rename (from|to)|copy (from|to)) .*([[:space:]]/|\.\./|/\.\.([[:space:]]|$))|^(new|old|deleted) file mode 120000|^(new|old) mode 120000'; then
    echo "$p refers to absolute or parent paths or symlinks"; exit 1
  fi
done

ver=$(sed -nE 's/^Version:[[:space:]]*([0-9.]+).*/\1/p' chromium.spec 2>/dev/null | head -1 || true)

for p in "${patches[@]}"; do
  out=$(sed -e "s/@VERSION@/$ver/g" "$root/packages/$pkg/$p" | patch -p1 -F0 --no-backup-if-mismatch 2>&1) || {
    echo "$p does not apply:"
    grep -vE '^patching file|^Hunk #[0-9]+ succeeded' <<< "$out" | head -60
    exit 1
  }
done
