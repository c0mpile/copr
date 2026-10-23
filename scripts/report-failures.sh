#!/usr/bin/bash
# Open a GitHub issue when a package's latest finished Copr build failed, and
# close it again once a later build succeeds.
# Env: COPR_PROJECT=<owner>/<project>  GH_TOKEN, GH_REPO (for gh)
set -euo pipefail
cd "$(dirname "$0")/.."
: "${COPR_PROJECT:?}"
default_project=$COPR_PROJECT
api=https://copr.fedorainfracloud.org/api_3
label=copr-build-failure

gh label create "$label" --color B60205 --description "Automated: Copr build failed" --force >/dev/null

# Optional Telegram message; needs TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID, otherwise skipped.
notify() {
  [[ -n ${TELEGRAM_BOT_TOKEN:-} && -n ${TELEGRAM_CHAT_ID:-} ]] || return 0
  curl -fsS -o /dev/null "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=$TELEGRAM_CHAT_ID" --data-urlencode "text=${1:0:3900}" \
    --data-urlencode disable_web_page_preview=true || echo "telegram notification failed" >&2
}

if [[ ${TEST_TELEGRAM:-false} == true ]]; then
  [[ -n ${TELEGRAM_BOT_TOKEN:-} && -n ${TELEGRAM_CHAT_ID:-} ]] || { echo "Telegram secrets are not set" >&2; exit 1; }
  curl -sS "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=$TELEGRAM_CHAT_ID" --data-urlencode "text=Copr build notifier test" |
    python3 -I -c "import json,sys; d=json.load(sys.stdin); print('telegram ok' if d['ok'] else 'telegram error %s: %s' % (d['error_code'], d['description'])); sys.exit(0 if d['ok'] else 1)"
  exit
fi

json() { python3 -I -c "import json,sys; d=json.load(sys.stdin); $1"; }

while read -r pkg _ _ _ project; do
  [[ -z $pkg || $pkg == \#* ]] && continue
  COPR_PROJECT=${project:-$default_project}
  owner=${COPR_PROJECT%/*}; proj=${COPR_PROJECT#*/}

  # Latest build that has finished one way or the other.
  read -r id state < <(curl -fsS "$api/build/list/?ownername=$owner&projectname=$proj&packagename=$pkg&limit=10&order=id&order_type=DESC" |
    json "
for b in d['items']:
    if b['state'] in ('succeeded', 'failed'):
        print(b['id'], b['state']); break
else:
    print('0 none')")
  [[ $id != 0 ]] || { echo "$pkg: no finished builds yet"; continue; }

  title="Copr build failed: $pkg (build $id)"
  open=$(gh issue list --label "$label" --state open --search "\"$pkg\" in:title" --json number,title --jq '.[] | "\(.number)\t\(.title)"')

  if [[ $state == succeeded ]]; then
    while IFS=$'\t' read -r num t; do
      [[ -n $num ]] || continue
      echo "$pkg: build $id succeeded, closing #$num"
      gh issue close "$num" --comment "Build $id succeeded: https://copr.fedorainfracloud.org/coprs/$COPR_PROJECT/build/$id/" >/dev/null
      notify "Copr build recovered: $pkg (build $id)
https://copr.fedorainfracloud.org/coprs/$COPR_PROJECT/build/$id/"
    done <<< "$open"
    continue
  fi

  if gh issue list --label "$label" --state all --search "\"$title\" in:title" --json title --jq '.[].title' | grep -qxF "$title"; then
    echo "$pkg: build $id failed (already reported)"; continue
  fi

  # Failing chroots and the interesting log lines.
  details=""
  for chroot in $(curl -fsS "$api/build/$id" | json "print(' '.join(d['chroots']))"); do
    cstate=$(curl -fsS "$api/build-chroot/$id/$chroot" | json "print(d['state'])")
    [[ $cstate == failed ]] || continue
    base=https://download.copr.fedorainfracloud.org/results/$COPR_PROJECT/$chroot/$(printf %08d "$id")-$pkg
    errs=$(curl -fsSL "$base/builder-live.log.gz" 2>/dev/null | gunzip 2>/dev/null |
      grep -E "ERROR: |error: |Dependency .* not found|No match for|Problem:|nothing provides|File not found|Installed .* unpackaged" |
      grep -vE "Werror|-error|Exception\(|Command failed|Bad exit status|Copr build error" | head -6 | cut -c1-300 || true)
    details+=$'\n'"**$chroot** ([log]($base/builder-live.log.gz))"$'\n```\n'"${errs:-see log}"$'\n```\n'
  done
  if [[ -z $details ]]; then   # failed before any chroot ran: SRPM stage
    base=https://download.copr.fedorainfracloud.org/results/$COPR_PROJECT/srpm-builds/$(printf %08d "$id")
    errs=$(curl -fsSL "$base/builder-live.log.gz" 2>/dev/null | gunzip 2>/dev/null | tail -8 | cut -c1-300 || true)
    details=$'\n'"**SRPM generation** ([log]($base/builder-live.log.gz))"$'\n```\n'"${errs:-see log}"$'\n```\n'
  fi

  echo "$pkg: build $id failed, opening issue"
  gh issue create --label "$label" --title "$title" --body "Build: https://copr.fedorainfracloud.org/coprs/$COPR_PROJECT/build/$id/
$details
Opened automatically; it closes itself when a later build of $pkg succeeds."
  notify "Copr build failed: $pkg (build $id)
https://copr.fedorainfracloud.org/coprs/$COPR_PROJECT/build/$id/
$(sed -e 's/\*\*//g' -e '/^```/d' <<< "$details" | head -20)"
done < packages/upstreams.conf
