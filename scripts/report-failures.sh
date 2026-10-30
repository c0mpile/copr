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

# Tell the owner once when the autofix agent has pushed a fix and opened a PR for a reported failure.
# A hidden marker comment on the issue records that the message went out.
notify_fix_pr() {
  local pkg=$1 id=$2 pr sha num
  read -r pr sha < <(gh pr list --state open --search "\"$pkg: fix Copr build $id\" in:title" --limit 1 --json url,headRefOid --jq '.[0] | "\(.url) \(.headRefOid)"' 2>/dev/null) || return 0
  [[ -n ${pr:-} && ${pr} != null && -n ${sha:-} ]] || return 0
  num=$(gh issue list --label "$label" --state open --search "\"Copr build failed: $pkg (build $id)\" in:title" --json number --jq '.[0].number // empty') || return 0
  [[ -n $num ]] || return 0
  ! gh issue view "$num" --json comments --jq '.comments[].body' | grep -qF 'autofix-pr-notified' || return 0
  gh issue comment "$num" --body "<!-- autofix-pr-notified -->Autofix pushed a fix and opened $pr for review." > /dev/null || return 0
  echo "$pkg: fix PR $pr is open, notifying"
  notify "Autofix committed a fix for $pkg (build $id) and opened a PR for you to review and merge:
$pr
head $sha
Reply \"merge\" to this message to merge it."
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

  # poll.sh found that the spec patches no longer apply and submitted no build. The issue uses the same title
  # shape as a build failure (the autofix script parses "(build N)"; N is the marker's timestamp here) and stays
  # open until the marker is removed by a poll that finds the patches applying again.
  marker=state/$pkg.patchfail
  if [[ -f $marker ]]; then
    read -r fsha fts < "$marker"
    title="Copr build failed: $pkg (build $fts)"
    if gh issue list --label "$label" --state all --search "\"$title\" in:title" --json title --jq '.[].title' | grep -qxF "$title"; then
      echo "$pkg: patches do not apply to $fsha (already reported)"; notify_fix_pr "$pkg" "$fts"; continue
    fi
    echo "$pkg: patches do not apply to $fsha, opening issue"
    gh issue create --label "$label" --title "$title" --body "No Copr build was submitted: the patches in packages/$pkg no longer apply to Fedora's chromium package at \`$fsha\`. Any earlier build in $COPR_PROJECT stays available.

\`\`\`
$(tail -n +2 "$marker")
\`\`\`

Fedora's unmodified files at that commit are in \`state/$pkg.fedora/\`; see README.md, \"Patch drift\". Opened automatically; it closes itself once the patches apply again and a later build of $pkg succeeds."
    notify "Copr patches no longer apply: $pkg (Fedora chromium ${fsha:0:12}); no build submitted
$(tail -n +2 "$marker" | head -10)"
    continue
  fi

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
      # If an autofix PR was merged for the failed build, say what the agent did.
      failed=${t##*(build }; failed=${failed%)}
      fix=$(gh pr list --state merged --search "\"$pkg: fix Copr build $failed\" in:title" --limit 1 --json url,body --jq '.[] | .url + "\n" + .body' || true)
      steps=""
      if [[ -n $fix ]]; then
        steps=$'\n\n'"Fixed by automated PR: $(head -1 <<< "$fix")"$'\n'"$(sed -n '/^## What the agent did/,$p' <<< "$fix" | sed -e 1d -e 's/^    //' -e '/^$/d' | head -40)"
      fi
      notify "Copr build recovered: $pkg (build $id)
https://copr.fedorainfracloud.org/coprs/$COPR_PROJECT/build/$id/$steps"
    done <<< "$open"
    continue
  fi

  if gh issue list --label "$label" --state all --search "\"$title\" in:title" --json title --jq '.[].title' | grep -qxF "$title"; then
    echo "$pkg: build $id failed (already reported)"; notify_fix_pr "$pkg" "$id"; continue
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
