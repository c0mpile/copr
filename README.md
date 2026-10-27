# Git-snapshot Copr repo

Packages live in `c0mpile/builds` (Fedora: the `-git` snapshots plus uzdoom, voicestudio, doomrunner, 64gram) and `c0mpile/el10` (EL10: unar).

EL10 has no GCC Objective-C compiler, so `unar` is built with clang against the GNUstep runtime, which the `el10` project also builds: `libobjc2`, `gnustep-make`, `gnustep-base`. These are pinned to a version in `upstreams.conf` (`pinned` mode, version in the branch column) and built in file order, each after the previous. A package can name its own Copr project in the 5th column of `upstreams.conf`.

- `packages/upstreams.conf` – upstream repo + branch per package
- `packages/<pkg>/<pkg>.spec` – spec templates (`@VERSION@ @COMMIT@ @STAMP@` filled in at SRPM time)
- `.copr/Makefile` + `scripts/make-srpm.sh` – Copr `make_srpm` hook: clones upstream HEAD, vendors crates (Rust), emits an SRPM
- `.github/workflows/report-failures.yml` + `scripts/report-failures.sh` – hourly: opens a GitHub issue when a package's latest finished Copr build failed (with the error lines), closes it when a later build succeeds
- `scripts/gen-buildrequires.py` – derives `BuildRequires` from upstream `meson.build` at SRPM time (`packages/<pkg>/deps.skip` lists names to ignore); specs keep only hand-written extras
- `scripts/prune-builds.sh` – deletes older Copr builds of a package once a newer version has successfully built
- `.github/workflows/poll.yml` – is scheduled every 15 minutes (GitHub often skips or delays scheduled runs, so real runs are less frequent), submits a Copr build for any package whose upstream HEAD (or packaging files) changed since `state/<pkg>`

## Setup
1. Create the Copr account, get the API config from https://copr.fedorainfracloud.org/api/
2. Push this repo to GitHub (public, so Copr can clone it).
3. `scripts/setup-copr.sh <user>/<project> https://github.com/<you>/<repo>.git`
4. Repo secret `COPR_CONFIG` = contents of `~/.config/copr`; repo variable `COPR_PROJECT` = `<user>/<project>`.
5. Run the workflow manually with `force` for the first builds.
