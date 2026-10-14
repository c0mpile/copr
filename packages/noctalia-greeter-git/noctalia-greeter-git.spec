%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

%global up noctalia-greeter
Name:           noctalia-greeter-git
Version:        @VERSION@
Release:        0.1.%{stamp}git%{shortcommit}%{?dist}
Summary:        greetd login screen matching the Noctalia shell
License:        MIT
URL:            https://github.com/noctalia-dev/noctalia-greeter
Provides:       noctalia-greeter = %{version}-%{release}
Conflicts:      noctalia-greeter
Conflicts:      noctalia-greeter-nightly
Source0:        %{up}-%{commit}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-ft)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pangoft2)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(wlroots-0.20)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libwebp)
Requires:       greetd

%description
A greetd login screen that matches the look of the Noctalia shell, running in
a bundled wlroots compositor. Git snapshot build.

%files
%license LICENSE
%doc README.md
%{_bindir}/*
%{_datadir}/noctalia-greeter/
%{_datadir}/polkit-1/actions/*
%{_prefix}/lib/tmpfiles.d/noctalia-greeter.conf

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
