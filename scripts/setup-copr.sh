#!/usr/bin/bash
# One-time: create the Copr project and register the five packages.
# Usage: setup-copr.sh <owner>/<project> <clone-url-of-this-repo>
set -euo pipefail
proj=$1; url=$2
copr-cli create "${proj#*/}" \
  --chroot fedora-44-x86_64 --chroot fedora-44-aarch64 \
  --chroot fedora-rawhide-x86_64 --chroot fedora-rawhide-aarch64 \
  --description "Git snapshot builds of xwayland-satellite, umbriel, xdg-desktop-portal-umbriel, noctalia, noctalia-greeter"
while read -r pkg _; do
  [[ -z $pkg || $pkg == \#* ]] && continue
  copr-cli add-package-scm "$proj" --name "$pkg" --clone-url "$url" --commit main \
    --method make_srpm --spec "packages/$pkg/$pkg.spec" || true
done < "$(dirname "$0")/../packages/upstreams.conf"
