#!/usr/bin/env bash
# Delete older Copr builds of packages once a newer build has succeeded.
# Keeps the newest successful build and any in-progress/newer builds.
# Env: COPR_PROJECT=<owner>/<project> (default: c0mpile/builds)
# Usage: prune-builds.sh [--dry-run] [--all] [package ...]
set -euo pipefail
cd "$(dirname "$0")/.."

default_project=${COPR_PROJECT:-c0mpile/builds}
dry_run=0

args=()
for arg in "$@"; do
  if [[ $arg == "--dry-run" ]]; then
    dry_run=1
  elif [[ $arg == "--all" ]]; then
    :
  else
    args+=("$arg")
  fi
done

prune_query() {
  local owner=$1 proj=$2 pkg=$3
  python3 -I -c '
import sys, json, urllib.request

owner, proj, pkg = sys.argv[1], sys.argv[2], sys.argv[3]
api_base = "https://copr.fedorainfracloud.org/api_3"
builds = []
offset = 0

while True:
    url = f"{api_base}/build/list/?ownername={owner}&projectname={proj}&packagename={pkg}&limit=100&offset={offset}&order=id&order_type=DESC"
    req = urllib.request.Request(url, headers={"User-Agent": "copr-pruner"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
    except Exception as e:
        print(f"error querying builds: {e}", file=sys.stderr)
        sys.exit(1)
    items = data.get("items", [])
    builds.extend(items)
    if len(items) < 100:
        break
    offset += 100

newest_succ = next((b for b in builds if b.get("state") == "succeeded"), None)
if not newest_succ:
    sys.exit(0)

succ_id = newest_succ["id"]
active_states = {"running", "pending", "starting", "waiting", "importing"}
to_delete = [b["id"] for b in builds if b["id"] < succ_id and b.get("state") not in active_states]

del_str = " ".join(str(i) for i in to_delete)
print(f"{succ_id}:{del_str}")
' "$owner" "$proj" "$pkg"
}

prune_package() {
  local pkg=$1 project=$2
  local owner=${project%/*} proj=${project#*/}
  local res succ_id del_str
  res=$(prune_query "$owner" "$proj" "$pkg")
  if [[ -z $res ]]; then
    echo "$pkg ($owner/$proj): no succeeded builds yet"
    return 0
  fi

  succ_id=${res%%:*}
  del_str=${res#*:}

  if [[ -z $del_str ]]; then
    echo "$pkg ($owner/$proj): up to date (build $succ_id)"
    return 0
  fi

  read -r -a to_delete <<< "$del_str"
  echo "$pkg ($owner/$proj): newest succeeded is $succ_id; pruning ${#to_delete[@]} older build(s)..."

  if [[ $dry_run -eq 1 ]]; then
    echo "  [dry-run] would delete: ${to_delete[*]}"
    return 0
  fi

  local i batch
  for ((i = 0; i < ${#to_delete[@]}; i += 50)); do
    batch=("${to_delete[@]:i:50}")
    copr-cli delete-build "${batch[@]}" || echo "::warning::failed to delete builds ${batch[*]}"
  done
}

if [[ ${#args[@]} -gt 0 ]]; then
  for pkg in "${args[@]}"; do
    proj=$(awk -v p="$pkg" '$1 == p { print $5 }' packages/upstreams.conf)
    prune_package "$pkg" "${proj:-$default_project}"
  done
else
  while read -r pkg _ _ _ project; do
    [[ -z $pkg || $pkg == \#* ]] && continue
    prune_package "$pkg" "${project:-$default_project}"
  done < packages/upstreams.conf
fi
