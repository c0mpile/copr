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
Recommends:     xwayland-satellite

%description
Umbriel is a Wayland compositor built on wlroots, from the Noctalia project.
Git snapshot build.

%files
%license LICENSE
%doc README.md
%{_bindir}/*
%{_datadir}/umbriel/
%{_datadir}/wayland-sessions/umbriel.desktop
%{_prefix}/lib/systemd/user/*

%prep
%autosetup -n %{up}-%{commit}

%build
%meson --buildtype=release -Dtests=disabled
%meson_build

%install
%meson_install

%changelog
* Wed Oct 14 2026 c0mpile <16279275+c0mpile@users.noreply.github.com> - 0-0.1
- Automated git snapshot build
