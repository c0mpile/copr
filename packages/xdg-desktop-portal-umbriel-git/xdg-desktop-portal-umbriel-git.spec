%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

%global up xdg-desktop-portal-umbriel
Name:           xdg-desktop-portal-umbriel-git
Version:        @VERSION@^%{stamp}git%{shortcommit}
Release:        1%{?dist}
Summary:        xdg-desktop-portal backend for the Umbriel compositor
License:        MIT
URL:            https://github.com/noctalia-dev/xdg-desktop-portal-umbriel
Provides:       xdg-desktop-portal-umbriel = %{version}-%{release}
Conflicts:      xdg-desktop-portal-umbriel
Conflicts:      xdg-desktop-portal-umbriel-nightly
Source0:        %{up}-%{commit}.tar.gz


BuildRequires:  git
BuildRequires:  gcc-c++
BuildRequires:  meson >= 1.3
BuildRequires:  ninja-build
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(gtk4) >= 4.12
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(sdbus-c++) >= 2.0
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.39
BuildRequires:  /usr/bin/wayland-scanner
BuildRequires:  systemd-rpm-macros

Requires:       xdg-desktop-portal
Requires:       pipewire
Provides:       xdg-desktop-portal-umbriel = %{version}-%{release}
Conflicts:      xdg-desktop-portal-umbriel
Supplements:    umbriel
Supplements:    umbriel-git

%description
xdg-desktop-portal backend for the Umbriel compositor (screen capture and
sharing). Git snapshot build.

%files -f %{_builddir}/%{name}.files
%license LICENSE
%doc README.md
%config %{_datadir}/xdg-desktop-portal/umbriel-portals.conf
%{_libexecdir}/xdg-desktop-portal-umbriel
%{_libexecdir}/umbriel-share-picker
%{_datadir}/xdg-desktop-portal/portals/umbriel.portal
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.desktop.umbriel.service
%{_userunitdir}/xdg-desktop-portal-umbriel.service

%prep
%autosetup -n %{up}-%{commit}

# Upstream tarball has no .git; stamp the commit into the version string
sed -i "s/'unknown'/'%{shortcommit}'/g" meson.build

%build
%meson -Dpicker=enabled
%meson_build

%install
%meson_install
# Package whatever upstream installs, so new files don't fail the build as unpackaged
find %{buildroot} -mindepth 1 \( -type f -o -type l \) ! -path '%{buildroot}%{_datadir}/xdg-desktop-portal/umbriel-portals.conf' -printf '/%%P\n' > %{_builddir}/%{name}.files

%post
%systemd_user_post xdg-desktop-portal-umbriel.service

%preun
%systemd_user_preun xdg-desktop-portal-umbriel.service

%postun
%systemd_user_postun_with_restart xdg-desktop-portal-umbriel.service

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - 0-0.1
- Automated git snapshot build
