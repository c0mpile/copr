#!/usr/bin/bash
# Drop BuildRequires that nothing in current Fedora rawhide provides (renamed or
# retired -devel packages), so a stale hand-written line doesn't fail every chroot.
# If the repo query itself fails the line is kept.
# Usage: prune-buildrequires.sh <spec>
set -uo pipefail
spec=$1
tmp=$(mktemp)
re='^BuildRequires:[[:space:]]+([^[:space:](]+)'
while IFS= read -r line; do
  if [[ $line =~ $re ]]; then
    dep=${BASH_REMATCH[1]}
    if out=$(dnf5 -q repoquery --releasever=rawhide --whatprovides "$dep" 2>/dev/null) && [[ -z $out ]]; then
      echo "prune-buildrequires: dropping '$dep' (not provided by rawhide)" >&2
      continue
    fi
  fi
  printf '%s\n' "$line"
done < "$spec" > "$tmp"
cat "$tmp" > "$spec"; rm -f "$tmp"
