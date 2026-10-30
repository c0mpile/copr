#!/usr/bin/bash
# One-time: create the isolated ungoogled-chromium Copr project (so high-performance builders can be
# requested for it alone) and register the package, built with Copr's "custom" method.
# The registered script is a template; poll.sh uploads a rendered, commit-pinned copy before each build.
# Usage: setup-ungoogled-chromium-copr.sh [<owner>/<project>]
set -euo pipefail
proj=${1:-c0mpile/ungoogled-chromium}
cd "$(dirname "$0")/.."
copr-cli create "${proj#*/}" \
  --chroot epel-9-x86_64 --chroot epel-10-x86_64 \
  --chroot fedora-44-x86_64 --chroot fedora-45-x86_64 --chroot fedora-rawhide-x86_64 \
  --description "Automatically updated release builds of Ungoogled Chromium, based on Fedora's chromium package" \
  --instructions "dnf copr enable ${proj}"
copr-cli add-package-custom "$proj" --name ungoogled-chromium \
  --script packages/ungoogled-chromium/copr_script.sh --script-builddeps "git rpkg" --timeout 108000
