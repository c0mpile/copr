#!/usr/bin/bash
# Compare upstream HEAD (+ our packaging files) with the last triggered build
# and submit a Copr SCM build for every package that changed.
# Packages may name their own Copr project in the 5th column of upstreams.conf; otherwise COPR_PROJECT is used.
# Env: COPR_PROJECT=<owner>/<project>  CLONE_URL=<this repo's clone url>  FORCE=1 to rebuild all
set -euo pipefail
cd "$(dirname "$0")/.."

: "${COPR_PROJECT:?}" "${CLONE_URL:?}"
changed=0
MAX_RETRIES=${MAX_RETRIES:-3}
# Packages with their own project build in file order, each after the previous one (they depend on each other).
declare -A last

# State of the newest Copr build of a package (failed, succeeded, running, ...), or "unknown".
newest_state() {
  curl -fsS --retry 3 "https://copr.fedorainfracloud.org/api_3/build/list/?ownername=${1%/*}&projectname=${1#*/}&packagename=$2&limit=1&order=id&order_type=DESC" |
    python3 -I -c "import json,sys; i=json.load(sys.stdin)['items']; print(i[0]['state'] if i else 'none')" 2>/dev/null || echo unknown
}

while read -r pkg url branch mode project; do
  [[ -z $pkg || $pkg == \#* ]] && continue
  read -r _ head < <(scripts/resolve-upstream.sh "$url" "$branch" "${mode:-head}") || true
  [[ -n ${head:-} ]] || { echo "::warning::could not resolve $pkg"; continue; }
  pkgsum=$(cat ".copr/Makefile" scripts/make-srpm.sh scripts/resolve-upstream.sh scripts/gen-buildrequires.py "packages/$pkg/"* | sha256sum | cut -c1-12)
  want="$head $pkgsum"
  have=$(cat "state/$pkg" 2>/dev/null || true)

  retry=0; tries=0
  if [[ ${FORCE:-0} != 1 && $want == "$have" ]]; then
    # Already submitted for this version. Builds can fail for reasons outside our control (Copr
    # builder timeouts), so resubmit when the newest build failed, a few times per version.
    rw=; rn=0
    IFS='|' read -r rw rn < "state/$pkg.retries" 2>/dev/null || true
    [[ $rw == "$want" ]] && tries=${rn:-0}
    if [[ $(newest_state "${project:-$COPR_PROJECT}" "$pkg") == failed && $tries -lt $MAX_RETRIES ]]; then
      retry=1
      echo "$pkg: newest build failed, retrying ($((tries + 1))/$MAX_RETRIES)"
    else
      echo "$pkg: up to date ($head)"
      continue
    fi
  else
    echo "$pkg: building $head (was: ${have:-none})"
  fi
  after=()
  [[ -z ${project:-} || -z ${last[${project:-}]:-} ]] || after=(--after-build-id "${last[$project]}")
  out=$(copr-cli buildscm "${project:-$COPR_PROJECT}" --nowait "${after[@]}" \
    --clone-url "$CLONE_URL" --commit "${PACKAGING_REF:-main}" \
    --method make_srpm --spec "packages/$pkg/$pkg.spec")
  echo "$out"
  [[ -z ${project:-} ]] || last[$project]=$(grep -oE 'Created builds: [0-9]+' <<< "$out" | grep -oE '[0-9]+')
  echo "$want" > "state/$pkg"
  if [[ $retry == 1 ]]; then echo "$want|$((tries + 1))" > "state/$pkg.retries"; else rm -f "state/$pkg.retries"; fi
  changed=1
done < packages/upstreams.conf

echo "changed=$changed" >> "${GITHUB_OUTPUT:-/dev/null}"
