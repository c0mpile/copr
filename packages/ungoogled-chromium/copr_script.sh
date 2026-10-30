#!/bin/bash -x
# Copr "custom" method script. scripts/render-copr-script.sh fills in the @...@ placeholders (pinned
# commits) before it is uploaded to Copr. It runs in a scratch directory, whose contents become the
# SRPM inputs.
set -euo pipefail

# Our packaging repo, for the patches (modify.patch, rename.patch, use-system-python.patch)
git clone @PACKAGING_URL@ packaging
git -C packaging checkout --detach @PACKAGING_COMMIT@

# Fedora's chromium package, which this is based on
git clone https://src.fedoraproject.org/rpms/chromium.git chromium
git -C chromium checkout --detach @FEDORA_COMMIT@

# Download chromium-%{version}-clean.tar.xz from Fedora's lookaside cache
rpkg --path ./chromium sources

# Patch the spec file to build with the ungoogled-chromium patches
patch -d ./chromium -p1 < packaging/packages/ungoogled-chromium/modify.patch

# Rename files that are called chromium-browser to ungoogled-chromium to avoid name clashes
patch -d ./chromium -p1 < packaging/packages/ungoogled-chromium/rename.patch

# Everything the spec needs goes next to it for the Copr build system to find
mv ./chromium/* .
cp packaging/packages/ungoogled-chromium/use-system-python.patch .
