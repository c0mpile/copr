#!/usr/bin/bash
# Compare upstream HEAD (+ our packaging files) with the last triggered build
# and submit a Copr SCM build for every package that changed.
# Packages may name their own Copr project in the 5th column of upstreams.conf; otherwise COPR_PROJECT is used.
# Env: COPR_PROJECT=<owner>/<project>  CLONE_URL=<this repo's clone url>  FORCE=1 to rebuild all
set -euo pipefail
cd "$(dirname "$0")/.."

: "${COPR_PROJECT:?}" "${CLONE_URL:?}"
changed=0
# Packages with their own project build in file order, each after the previous one (they depend on each other).
declare -A last

while read -r pkg url branch mode project; do
  [[ -z $pkg || $pkg == \#* ]] && continue
  read -r _ head < <(scripts/resolve-upstream.sh "$url" "$branch" "${mode:-head}") || true
  [[ -n ${head:-} ]] || { echo "::warning::could not resolve $pkg"; continue; }
  pkgsum=$(cat ".copr/Makefile" scripts/make-srpm.sh scripts/resolve-upstream.sh scripts/gen-buildrequires.py "packages/$pkg/"* | sha256sum | cut -c1-12)
  want="$head $pkgsum"
  have=$(cat "state/$pkg" 2>/dev/null || true)

  if [[ ${FORCE:-0} != 1 && $want == "$have" ]]; then
    echo "$pkg: up to date ($head)"
    continue
  fi
  echo "$pkg: building $head (was: ${have:-none})"
  after=()
  [[ -z ${project:-} || -z ${last[${project:-}]:-} ]] || after=(--after-build-id "${last[$project]}")
  out=$(copr-cli buildscm "${project:-$COPR_PROJECT}" --nowait "${after[@]}" \
    --clone-url "$CLONE_URL" --commit "${PACKAGING_REF:-main}" \
    --method make_srpm --spec "packages/$pkg/$pkg.spec")
  echo "$out"
  [[ -z ${project:-} ]] || last[$project]=$(grep -oE 'Created builds: [0-9]+' <<< "$out" | grep -oE '[0-9]+')
  echo "$want" > "state/$pkg"
  changed=1
done < packages/upstreams.conf

echo "changed=$changed" >> "${GITHUB_OUTPUT:-/dev/null}"
