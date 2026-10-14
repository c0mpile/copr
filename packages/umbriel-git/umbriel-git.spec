%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

%global up umbriel
Name:           umbriel-git
Version:        @VERSION@
Release:        0.1.%{stamp}git%{shortcommit}%{?dist}
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
BuildRequires:  pkgconfig(wayland-server) >= 1.24
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.47
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.1
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput) >= 1.23
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-ewmh)
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
* Wed Oct 14 2026 c0mpile <16279275+c0mpile@users.noreply.github.com> - 0-0.1
- Automated git snapshot build
