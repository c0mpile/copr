%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

Name:           xdg-desktop-portal-umbriel
Version:        @VERSION@
Release:        0.1.%{stamp}git%{shortcommit}%{?dist}
Summary:        xdg-desktop-portal backend for the Umbriel compositor
License:        MIT
URL:            https://github.com/noctalia-dev/xdg-desktop-portal-umbriel
Source0:        %{name}-%{commit}.tar.gz

BuildRequires:  meson >= 1.3
BuildRequires:  gcc-c++
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
%{_datadir}/xdg-desktop-portal/
%{_datadir}/dbus-1/services/*
%{_prefix}/lib/systemd/user/*

%prep
%autosetup -n %{name}-%{commit}

%build
%meson --buildtype=release 
%meson_build

%install
%meson_install

%changelog
* Wed Oct 14 2026 c0mpile <16279275+c0mpile@users.noreply.github.com> - 0-0.1
- Automated git snapshot build
