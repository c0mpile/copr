%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

%global up xdg-desktop-portal-umbriel
Name:           xdg-desktop-portal-umbriel-git
Version:        @VERSION@
Release:        0.1.%{stamp}git%{shortcommit}%{?dist}
Summary:        xdg-desktop-portal backend for the Umbriel compositor
License:        MIT
URL:            https://github.com/noctalia-dev/xdg-desktop-portal-umbriel
Provides:       xdg-desktop-portal-umbriel = %{version}-%{release}
Conflicts:      xdg-desktop-portal-umbriel
Conflicts:      xdg-desktop-portal-umbriel-nightly
Source0:        %{up}-%{commit}.tar.gz

BuildRequires:  meson >= 1.3
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  git
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(sdbus-c++) >= 2.0
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.39
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(gtk4) >= 4.12
Requires:       xdg-desktop-portal
Supplements:    umbriel

%description
xdg-desktop-portal backend for the Umbriel compositor (screen capture and
sharing). Git snapshot build.

%files
%license LICENSE
%doc README.md
%{_libexecdir}/*
%{_datadir}/xdg-desktop-portal/portals/umbriel.portal
%config %{_datadir}/xdg-desktop-portal/umbriel-portals.conf
%{_datadir}/dbus-1/services/*
%{_userunitdir}/*

%prep
%autosetup -n %{up}-%{commit}

# Upstream tarball has no .git; stamp the commit into the version string
sed -i "s/'unknown'/'%{shortcommit}'/g" meson.build

%build
%meson --buildtype=release 
%meson_build

%install
%meson_install

%post
%systemd_user_post xdg-desktop-portal-umbriel.service

%preun
%systemd_user_preun xdg-desktop-portal-umbriel.service

%postun
%systemd_user_postun xdg-desktop-portal-umbriel.service

%changelog
* Wed Oct 14 2026 c0mpile <16279275+c0mpile@users.noreply.github.com> - 0-0.1
- Automated git snapshot build
