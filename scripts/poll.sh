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
script_tmp=$(mktemp)
trap 'rm -f "$script_tmp"' EXIT
# Packages with their own project build in file order, each after the previous one (they depend on each other).
declare -A last

# State of the newest Copr build of a package (failed, succeeded, running, ...), or "unknown".
newest_state() {
  curl -fsS --retry 3 "https://copr.fedorainfracloud.org/api_3/build/list/?ownername=${1%/*}&projectname=${1#*/}&packagename=$2&limit=1&order=id&order_type=DESC" |
    python3 -I -c "import json,sys; i=json.load(sys.stdin)['items']; print(i[0]['state'] if i else 'none')" 2>/dev/null || echo unknown
}

# Chroots that failed in the newest build of a package, as "--chroot X" arguments. Empty when the
# failure happened before any chroot started (SRPM stage), which means rebuild everything.
failed_chroot_args() {
  local api=https://copr.fedorainfracloud.org/api_3 id c state
  id=$(curl -fsS --retry 3 "$api/build/list/?ownername=${1%/*}&projectname=${1#*/}&packagename=$2&limit=1&order=id&order_type=DESC" |
    python3 -I -c "import json,sys; print(json.load(sys.stdin)['items'][0]['id'])" 2>/dev/null) || return 0
  for c in $(curl -fsS --retry 3 "$api/build/$id" | python3 -I -c "import json,sys; print(' '.join(json.load(sys.stdin)['chroots']))" 2>/dev/null); do
    state=$(curl -fsS --retry 3 "$api/build-chroot/$id/$c" | python3 -I -c "import json,sys; print(json.load(sys.stdin)['state'])" 2>/dev/null) || continue
    [[ $state != failed ]] || printf -- '--chroot %s ' "$c"
  done
}

while read -r pkg url branch mode project; do
  [[ -z $pkg || $pkg == \#* ]] && continue
  read -r _ head < <(scripts/resolve-upstream.sh "$url" "$branch" "${mode:-head}") || true
  [[ -n ${head:-} ]] || { echo "::warning::could not resolve $pkg"; continue; }
  pkgsum=$(cat ".copr/Makefile" scripts/make-srpm.sh scripts/resolve-upstream.sh scripts/gen-buildrequires.py "packages/$pkg/"* | sha256sum | cut -c1-12)
  want="$head $pkgsum"
  have=$(cat "state/$pkg" 2>/dev/null || true)

  retry=0; tries=0; chroots=()
  if [[ ${FORCE:-0} != 1 && $want == "$have" ]]; then
    # Already submitted for this version. Builds can fail for reasons outside our control (Copr
    # builder timeouts), so resubmit when the newest build failed, a few times per version.
    rw=; rn=0
    IFS='|' read -r rw rn 2>/dev/null < "state/$pkg.retries" || true
    [[ $rw == "$want" ]] && tries=${rn:-0}
    if [[ $(newest_state "${project:-$COPR_PROJECT}" "$pkg") == failed && $tries -lt $MAX_RETRIES ]]; then
      retry=1
      # shellcheck disable=SC2207
      chroots=($(failed_chroot_args "${project:-$COPR_PROJECT}" "$pkg"))
      echo "$pkg: newest build failed, retrying ($((tries + 1))/$MAX_RETRIES) ${chroots[*]}"
    else
      echo "$pkg: up to date ($head)"
      continue
    fi
  else
    echo "$pkg: building $head (was: ${have:-none})"
  fi
  if [[ -f packages/$pkg/copr_script.sh ]]; then
    # Spec patches can drift from Fedora's spec. Don't submit a build that is bound to fail; leave a marker
    # (plus the Fedora files the patches touch, for the autofix agent) in state/ for report-failures.sh to turn into an issue.
    rc=0; check=$(scripts/check-patches.sh "$pkg" "$url" "$branch" "$head" "$PWD/state/$pkg.fedora" 2>&1) || rc=$?
    if [[ $rc == 1 ]]; then
      # The timestamp doubles as the issue's pseudo build id; keep it while the failing commit stays the same.
      ts=$(date +%s); read -r ph pts 2>/dev/null < "state/$pkg.patchfail" || true
      [[ ${ph:-} != "$head" ]] || ts=$pts
      printf '%s %s\n%s\n' "$head" "$ts" "$check" > "state/$pkg.patchfail"
      echo "::warning::$pkg: patches do not apply to $head, not building"
      changed=1
      continue
    fi
    rm -rf "state/$pkg.patchfail" "state/$pkg.fedora"
  fi
  after=()
  [[ -z ${project:-} || -z ${last[${project:-}]:-} ]] || after=(--after-build-id "${last[$project]}")
  if [[ -f packages/$pkg/copr_script.sh ]]; then
    # Custom-method package (ungoogled-chromium): the script is stored in Copr, so upload a copy
    # pinned to the commits being built. Builds run up to Copr's 30h maximum.
    scripts/render-copr-script.sh "$pkg" "$head" "$CLONE_URL" > "$script_tmp"
    copr-cli edit-package-custom "${project:-$COPR_PROJECT}" --name "$pkg" \
      --script "$script_tmp" --script-builddeps "git rpkg" --timeout 108000
    out=$(copr-cli build-package "${project:-$COPR_PROJECT}" --name "$pkg" --nowait --timeout 108000 \
      "${after[@]}" "${chroots[@]}")
  else
    out=$(copr-cli buildscm "${project:-$COPR_PROJECT}" --nowait "${after[@]}" "${chroots[@]}" \
      --clone-url "$CLONE_URL" --commit "${PACKAGING_REF:-main}" \
      --method make_srpm --spec "packages/$pkg/$pkg.spec")
  fi
  echo "$out"
  [[ -z ${project:-} ]] || last[$project]=$(grep -oE 'Created builds: [0-9]+' <<< "$out" | grep -oE '[0-9]+')
  echo "$want" > "state/$pkg"
  if [[ $retry == 1 ]]; then echo "$want|$((tries + 1))" > "state/$pkg.retries"; else rm -f "state/$pkg.retries"; fi
  changed=1
done < packages/upstreams.conf

echo "changed=$changed" >> "${GITHUB_OUTPUT:-/dev/null}"
