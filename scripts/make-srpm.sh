#!/usr/bin/bash
# Build an SRPM for <pkg> from the current upstream HEAD.
# Usage: make-srpm.sh <pkg> <outdir>
set -euo pipefail

pkg=$1
outdir=$(realpath "$2")
root=$(cd "$(dirname "$0")/.." && pwd)

read -r _ url branch < <(grep -E "^${pkg}[[:space:]]" "$root/packages/upstreams.conf")
[[ -n ${url:-} ]] || { echo "unknown package $pkg" >&2; exit 1; }

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

git clone --quiet --branch "$branch" "$url" "$work/src"
cd "$work/src"
commit=$(git rev-parse HEAD)
# Commit timestamp keeps Release monotonic across builds.
stamp=$(git show -s --format=%cd --date=format-local:%Y%m%d%H%M%S HEAD)

# Base version from upstream metadata (falls back to 0).
version=
if [[ -f Cargo.toml ]]; then
  version=$(sed -nE '/^\[package\]/,/^\[/{s/^version *= *"([^"]+)".*/\1/p}' Cargo.toml | head -1)
elif [[ -f VERSION ]]; then
  version=$(tr -d '[:space:]' < VERSION)
else
  version=$(sed -nE "/^project\(/,/\)/{s/.*version *: *'([^']+)'.*/\1/p}" meson.build | head -1)
fi
# RPM versions can't contain '-'; drop any pre-release suffix into Release.
version=${version%%-*}
version=${version:-0}

name=$pkg-$commit
git archive --format=tar --prefix="$name/" HEAD | tar -x -C "$work"

# Rust: vendor crates now, since the mock build has no network.
if [[ -f Cargo.toml ]]; then
  (cd "$work/$name" && mkdir -p .cargo && cargo vendor --locked vendor > .cargo/config.toml)
fi

mkdir -p "$work/rpm"/{SOURCES,SRPMS}
tar -C "$work" -czf "$work/rpm/SOURCES/$name.tar.gz" "$name"
cp "$root/packages/$pkg/"* "$work/rpm/SOURCES/" 2>/dev/null || true
sed -e "s/@VERSION@/$version/" -e "s/@COMMIT@/$commit/" -e "s/@STAMP@/$stamp/" \
  "$root/packages/$pkg/$pkg.spec" > "$work/rpm/$pkg.spec"

rpmbuild -bs "$work/rpm/$pkg.spec" \
  --define "_topdir $work/rpm" --define "_sourcedir $work/rpm/SOURCES" \
  --define "_srcrpmdir $outdir"
