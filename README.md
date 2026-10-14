# Git-snapshot Copr repo

Packages (all suffixed `-git`): xwayland-satellite, umbriel, xdg-desktop-portal-umbriel, noctalia, noctalia-greeter.

- `packages/upstreams.conf` – upstream repo + branch per package
- `packages/<pkg>/<pkg>.spec` – spec templates (`@VERSION@ @COMMIT@ @STAMP@` filled in at SRPM time)
- `.copr/Makefile` + `scripts/make-srpm.sh` – Copr `make_srpm` hook: clones upstream HEAD, vendors crates (Rust), emits an SRPM
- `.github/workflows/report-failures.yml` + `scripts/report-failures.sh` – hourly: opens a GitHub issue when a package's latest finished Copr build failed (with the error lines), closes it when a later build succeeds
- `scripts/gen-buildrequires.py` – derives `BuildRequires` from upstream `meson.build` at SRPM time (`packages/<pkg>/deps.skip` lists names to ignore); specs keep only hand-written extras
- `.github/workflows/poll.yml` – runs every 2 hours (at :07), submits a Copr build for any package whose upstream HEAD (or packaging files) changed since `state/<pkg>`

## Setup
1. Create the Copr account, get the API config from https://copr.fedorainfracloud.org/api/
2. Push this repo to GitHub (public, so Copr can clone it).
3. `scripts/setup-copr.sh <user>/<project> https://github.com/<you>/<repo>.git`
4. Repo secret `COPR_CONFIG` = contents of `~/.config/copr`; repo variable `COPR_PROJECT` = `<user>/<project>`.
5. Run the workflow manually with `force` for the first builds.
