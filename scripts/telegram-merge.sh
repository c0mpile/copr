#!/usr/bin/bash
# Merge an autofix PR when the owner replies "merge" to its Telegram notification.
# Env: GH_TOKEN, GH_REPO (for gh), TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
# Stateless: pending updates are read, handled and then confirmed; a repeated "merge" finds the PR closed.
set -euo pipefail
: "${GH_REPO:?}" "${TELEGRAM_BOT_TOKEN:?}" "${TELEGRAM_CHAT_ID:?}"
tg=https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}

reply() { # <message_id> <text>
  curl -fsS -o /dev/null "$tg/sendMessage" --data-urlencode "chat_id=$TELEGRAM_CHAT_ID" \
    --data-urlencode "reply_to_message_id=$1" --data-urlencode "text=$2" || echo "telegram reply failed" >&2
}

updates=$(curl -fsS "$tg/getUpdates" --data-urlencode 'allowed_updates=["message"]' --data-urlencode timeout=0)

# Only the owner's private chat counts, and only a "merge" reply to one of the bot's own PR notifications.
# Output: <update_id> <message_id> <pr> <head sha>, or "<update_id>" alone for updates to skip.
requests=$(UPDATES=$updates python3 -I -c '
import json, os, re
chat = os.environ["TELEGRAM_CHAT_ID"]
url = re.escape("https://github.com/" + os.environ["GH_REPO"] + "/pull/")
pat = re.compile(r"^Autofix committed a fix for \S+ \(build \d+\) and opened a PR for you to review and merge:\n" + url + r"(\d+)\nhead ([0-9a-f]{40})\n", re.M)
for u in json.loads(os.environ["UPDATES"]).get("result", []):
    m = u.get("message") or {}
    r = m.get("reply_to_message") or {}
    ok = (str(m.get("chat", {}).get("id")) == chat and m.get("chat", {}).get("type") == "private"
          and str(m.get("from", {}).get("id")) == chat and (m.get("text") or "").strip().lower() == "merge"
          and r.get("from", {}).get("is_bot") is True)
    hit = pat.match(r.get("text") or "") if ok else None
    print(u["update_id"], *( [m["message_id"], hit.group(1), hit.group(2)] if hit else [] ))
' < /dev/null)

last=
while read -r uid mid pr sha; do
  [[ -n $uid ]] || continue
  last=$uid
  [[ -n ${pr:-} ]] || continue
  echo "merge requested for PR #$pr at $sha"
  if ! info=$(gh api "repos/$GH_REPO/pulls/$pr" --jq '[.state, .head.ref, .head.sha, .head.repo.full_name, .title] | @tsv'); then
    reply "$mid" "Could not read PR #$pr."; continue
  fi
  IFS=$'\t' read -r state ref head repo title <<< "$info"
  if [[ $state != open ]]; then reply "$mid" "PR #$pr is not open any more."; continue; fi
  if [[ ! $ref =~ ^fix/[A-Za-z0-9._+-]+-[0-9]+$ || $repo != "$GH_REPO" || ! $title =~ ^[A-Za-z0-9._+-]+:\ fix\ Copr\ build\ [0-9]+$ ]]; then
    reply "$mid" "PR #$pr is not an autofix PR, not merging."; continue
  fi
  if [[ $head != "$sha" ]]; then
    reply "$mid" "PR #$pr changed after that notification (now ${head:0:7}), not merging. Review it again."; continue
  fi
  if out=$(gh api -X PUT "repos/$GH_REPO/pulls/$pr/merge" -f sha="$sha" -f merge_method=squash --jq .message 2>&1); then
    gh api -X DELETE "repos/$GH_REPO/git/refs/heads/$ref" > /dev/null 2>&1 || true
    reply "$mid" "Merged PR #$pr."
  else
    reply "$mid" "Merging PR #$pr failed: ${out:0:300}"
  fi
done <<< "$requests"

# Confirm everything seen, so Telegram drops it.
[[ -z $last ]] || curl -fsS -o /dev/null "$tg/getUpdates" --data-urlencode "offset=$((last + 1))" --data-urlencode timeout=0
