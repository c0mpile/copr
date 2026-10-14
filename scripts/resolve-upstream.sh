#!/usr/bin/bash
# Resolve what to build for an upstream.
# Usage: resolve-upstream.sh <url> <branch> [head|release]
# Prints "<ref to clone> <identifier>":
#   head:    branch name + commit sha of the branch tip
#   release: highest dotted-version tag (5.0.3, v1.2) twice; rolling/pre-release tags are ignored
set -euo pipefail
url=$1; branch=${2:--}; mode=${3:-head}

case $mode in
  head)
    sha=$(git ls-remote "$url" "refs/heads/$branch" | cut -f1)
    [[ -n $sha ]] || exit 1
    echo "$branch $sha" ;;
  release)
    tag=$(git ls-remote --tags --refs "$url" | sed 's|.*refs/tags/||' |
          grep -E '^v?[0-9]+(\.[0-9]+)+$' | sort -V | tail -1)
    [[ -n $tag ]] || exit 1
    echo "$tag $tag" ;;
  *) echo "unknown mode $mode" >&2; exit 2 ;;
esac
