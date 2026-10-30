# Git-snapshot Copr repo

Packages live in `c0mpile/builds` (Fedora: the `-git` snapshots plus uzdoom, voicestudio, doomrunner, 64gram) and `c0mpile/el10` (EL10: unar).

Ungoogled Chromium has its own isolated project, `c0mpile/ungoogled-chromium` (el9, el10, Fedora 44, 45, rawhide), so that high-performance builders can be requested for it alone. It uses Copr's `custom` method: `packages/ungoogled-chromium/copr_script.sh` clones Fedora's `chromium` dist-git (rawhide) and applies the vendored `modify.patch`, `rename.patch` and `use-system-python.patch` (derived from wojnilowicz/ungoogled-chromium-copr, BSD-3-Clause, see `LICENSE.patches`), which add the ungoogled-chromium patches and rename the package. `poll.sh` rebuilds when Fedora's rawhide commit changes, but only once ungoogled-chromium has tagged that Chromium version; the commits being built are pinned in the script before it is uploaded (`scripts/render-copr-script.sh`). Builds time out after 30h. If Fedora's spec drifts so that a patch no longer applies, the build fails and `report-failures` opens an issue; fix the patches then. Create the project with `scripts/setup-ungoogled-chromium-copr.sh`.

EL10 has no GCC Objective-C compiler, so `unar` is built with clang against the GNUstep runtime, which the `el10` project also builds: `libobjc2`, `gnustep-make`, `gnustep-base`. These are pinned to a version in `upstreams.conf` (`pinned` mode, version in the branch column) and built in file order, each after the previous. A package can name its own Copr project in the 5th column of `upstreams.conf`.

- `packages/upstreams.conf` – upstream repo + branch per package
- `packages/<pkg>/<pkg>.spec` – spec templates (`@VERSION@ @COMMIT@ @STAMP@` filled in at SRPM time)
- `.copr/Makefile` + `scripts/make-srpm.sh` – Copr `make_srpm` hook: clones upstream HEAD, vendors crates (Rust), emits an SRPM
- `.github/workflows/report-failures.yml` + `scripts/report-failures.sh` – hourly: opens a GitHub issue when a package's latest finished Copr build failed (with the error lines), closes it when a later build succeeds
- `scripts/gen-buildrequires.py` – derives `BuildRequires` from upstream `meson.build` at SRPM time (`packages/<pkg>/deps.skip` lists names to ignore); specs keep only hand-written extras
- `scripts/prune-builds.sh` – deletes older Copr builds of a package once a newer version has successfully built
- `.github/workflows/poll.yml` – is scheduled every 15 minutes (GitHub often skips or delays scheduled runs, so real runs are less frequent), submits a Copr build for any package whose upstream HEAD (or packaging files) changed since `state/<pkg>`

### Patch drift (ungoogled-chromium)
Before submitting an ungoogled-chromium build, `poll.sh` dry-runs `modify.patch`, `rename.patch` and `use-system-python.patch` (`scripts/check-patches.sh`) against the Fedora commit it would build. If they don't apply, no build is submitted and the previous build stays; `poll.sh` leaves `state/ungoogled-chromium.patchfail` (the failing commit, a timestamp and the patch output) and `state/ungoogled-chromium.fedora/` (Fedora's unmodified files that the patches touch, at that commit, plus Chromium's `.gn` for `use-system-python.patch`). `report-failures.sh` then opens a `copr-build-failure` issue titled `Copr build failed: ungoogled-chromium (build <timestamp>)` and sends the Telegram message; the autofix agent picks it up like any other build failure.

To fix it, edit the hunks of `packages/ungoogled-chromium/modify.patch` (and `rename.patch` or `use-system-python.patch` if needed) so they apply to `state/ungoogled-chromium.fedora/`; keep every other change (`modify.patch` uses `@VERSION@` for the `Version:` context line). Do not touch `state/`. Verify with (the agent sandbox has `patch` but no network):

    rm -rf /tmp/t && cp -a state/ungoogled-chromium.fedora /tmp/t && cd /tmp/t
    ver=$(sed -nE 's/^Version:[[:space:]]*([0-9.]+).*/\1/p' chromium.spec | head -1)
    sed "s/@VERSION@/$ver/g" /work/packages/ungoogled-chromium/modify.patch | patch -p1 --dry-run   # then apply it for real
    patch -p1 --dry-run < /work/packages/ungoogled-chromium/rename.patch
    patch -p1 --dry-run < /work/packages/ungoogled-chromium/use-system-python.patch

or run `scripts/check-patches.sh ungoogled-chromium --local state/ungoogled-chromium.fedora` where bash is allowed. Patches are checked with fuzz 0, as `rpmbuild` applies them. The next poll re-checks, removes the marker, and builds.

## Setup
1. Create the Copr account, get the API config from https://copr.fedorainfracloud.org/api/
2. Push this repo to GitHub (public, so Copr can clone it).
3. `scripts/setup-copr.sh <user>/<project> https://github.com/<you>/<repo>.git`
4. Repo secret `COPR_CONFIG` = contents of `~/.config/copr`; repo variable `COPR_PROJECT` = `<user>/<project>`.
5. Run the workflow manually with `force` for the first builds.
