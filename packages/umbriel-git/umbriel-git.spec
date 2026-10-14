%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

%global up umbriel
Name:           umbriel-git
Version:        @VERSION@^%{stamp}git%{shortcommit}
Release:        1%{?dist}
Summary:        A Wayland compositor built on wlroots
License:        MIT
URL:            https://github.com/noctalia-dev/umbriel
Provides:       umbriel = %{version}-%{release}
Conflicts:      umbriel
Conflicts:      umbriel-nightly
Source0:        %{up}-%{commit}.tar.gz

BuildRequires:  meson >= 1.3
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  git
# Derived from upstream meson.build at SRPM time (scripts/gen-buildrequires.py)
# @GENERATED_BUILDREQUIRES@
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(xcb-render)
BuildRequires:  pkgconfig(jemalloc)
BuildRequires:  pkgconfig(sdbus-c++)
BuildRequires:  pkgconfig(md4c)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  systemd-rpm-macros
Requires:       xwayland-satellite
Requires:       xdg-desktop-portal-umbriel

%description
Umbriel is a Wayland compositor built on wlroots, from the Noctalia project.
Git snapshot build.

%files
%license LICENSE
%doc README.md
%{_bindir}/*
%config %{_datadir}/umbriel/config.toml
%{_datadir}/umbriel/
%{_datadir}/wayland-sessions/umbriel.desktop
%{_userunitdir}/*

%prep
%autosetup -n %{up}-%{commit}

# Upstream tarball has no .git; stamp the commit into the version string
sed -i "s/'unknown'/'%{shortcommit}'/g" meson.build

%build
%meson --buildtype=release -Dtests=disabled
%meson_build

%install
%meson_install --skip-subprojects

%post
%systemd_user_post umbriel.service

%preun
%systemd_user_preun umbriel.service

%postun
%systemd_user_postun umbriel.service

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - 0-0.1
- Automated git snapshot build
