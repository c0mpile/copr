#!/usr/bin/bash
# Resolve what to build for an upstream.
# Usage: resolve-upstream.sh <url> <branch> [head|release|ghrelease]
# Prints "<ref to clone> <identifier>":
#   head:    branch name + commit sha of the branch tip
#   release: highest dotted-version tag (5.0.3, v1.2) twice; rolling/pre-release tags are ignored
#   ghrelease: tag of the repo's latest non-prerelease GitHub release (for repos whose tags are not
#              a clean version sequence); read from the /releases/latest redirect, no API needed
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
  ghrelease)
    repo=${url%.git}
    final=$(curl -fsSIL --retry 3 -o /dev/null -w '%{url_effective}' "$repo/releases/latest")
    tag=${final##*/releases/tag/}
    [[ $final == */releases/tag/* && -n $tag ]] || exit 1
    echo "$tag $tag" ;;
  *) echo "unknown mode $mode" >&2; exit 2 ;;
esac
