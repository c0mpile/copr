# Copr "make_srpm" entry point. Copr calls:
#   make -f .copr/Makefile srpm outdir=<dir> spec=packages/<name>/<name>.spec
spec ?=
outdir ?= .
pkg = $(basename $(notdir $(spec)))

srpm:
	dnf -y install git rpm-build cargo rust tar gzip meson python3
	./scripts/make-srpm.sh $(pkg) $(outdir)
