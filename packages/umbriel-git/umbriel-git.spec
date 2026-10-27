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
BuildRequires:  ninja-build
BuildRequires:  nlohmann-json-devel
# Derived from upstream meson.build at SRPM time (scripts/gen-buildrequires.py)
# @GENERATED_BUILDREQUIRES@
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(jemalloc)
BuildRequires:  pkgconfig(lcms2)
BuildRequires:  pkgconfig(libdisplay-info) >= 0.3.0
BuildRequires:  pkgconfig(libdrm) >= 2.4.129
BuildRequires:  pkgconfig(libeis-1.0) >= 1.3
BuildRequires:  pkgconfig(libinput) >= 1.27
BuildRequires:  pkgconfig(libsystemd) >= 243
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pixman-1) >= 0.43.0
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.47
BuildRequires:  pkgconfig(wayland-server) >= 1.24
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.1
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-ewmh)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  systemd-rpm-macros
Recommends:     xdg-desktop-portal-umbriel

%description
Umbriel is a Wayland compositor built on wlroots, from the Noctalia project.
Git snapshot build.

%files -f %{_builddir}/%{name}.files
%license LICENSE
%doc README.md
%config %{_datadir}/umbriel/config.toml

%prep
%autosetup -n %{up}-%{commit}

# Upstream tarball has no .git; stamp the commit into the version string
sed -i "s/'unknown'/'%{shortcommit}'/g" meson.build

%build
%meson --buildtype=release -Dtests=disabled
%meson_build

%install
%meson_install --skip-subprojects
# Package whatever upstream installs, so new files don't fail the build as unpackaged
find %{buildroot} -mindepth 1 \( -type f -o -type l \) ! -path '%{buildroot}%{_datadir}/umbriel/config.toml' -printf '/%%P\n' > %{_builddir}/%{name}.files
find %{buildroot}%{_datadir} -type d -path '%{buildroot}%{_datadir}/umbriel*' -printf '%%%%dir %{_datadir}/%%P\n' >> %{_builddir}/%{name}.files

%post
%systemd_user_post umbriel.service

%preun
%systemd_user_preun umbriel.service

%postun
%systemd_user_postun umbriel.service

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - 0-0.1
- Automated git snapshot build
