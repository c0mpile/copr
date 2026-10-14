# Git-snapshot Copr repo

Packages (all suffixed `-git`): xwayland-satellite, umbriel, xdg-desktop-portal-umbriel, noctalia, noctalia-greeter.

- `packages/upstreams.conf` – upstream repo + branch per package
- `packages/<pkg>/<pkg>.spec` – spec templates (`@VERSION@ @COMMIT@ @STAMP@` filled in at SRPM time)
- `.copr/Makefile` + `scripts/make-srpm.sh` – Copr `make_srpm` hook: clones upstream HEAD, vendors crates (Rust), emits an SRPM
- `.github/workflows/poll.yml` – runs at :07 and :37, submits a Copr build for any package whose upstream HEAD (or packaging files) changed since `state/<pkg>`

## Setup
1. Create the Copr account, get the API config from https://copr.fedorainfracloud.org/api/
2. Push this repo to GitHub (public, so Copr can clone it).
3. `scripts/setup-copr.sh <user>/<project> https://github.com/<you>/<repo>.git`
4. Repo secret `COPR_CONFIG` = contents of `~/.config/copr`; repo variable `COPR_PROJECT` = `<user>/<project>`.
5. Run the workflow manually with `force` for the first builds.
