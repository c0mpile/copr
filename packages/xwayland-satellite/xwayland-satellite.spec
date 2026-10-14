%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

Name:           xwayland-satellite
Version:        @VERSION@
Release:        0.1.%{stamp}git%{shortcommit}%{?dist}
Summary:        Rootless Xwayland integration for any Wayland compositor
License:        MPL-2.0 AND MIT AND Apache-2.0
URL:            https://github.com/Supreeeme/xwayland-satellite
Source0:        %{name}-%{commit}.tar.gz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang-devel
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-cursor)
BuildRequires:  pkgconfig(fontconfig)
Requires:       xorg-x11-server-Xwayland >= 23.1

%description
xwayland-satellite grants rootless Xwayland integration to any Wayland
compositor implementing xdg_wm_base and viewporter. Git snapshot build.

%prep
%autosetup -n %{name}-%{commit}

%build
export CARGO_HOME=$PWD/.cargo-home
cargo build --release --offline --features systemd

%install
install -Dpm0755 target/release/xwayland-satellite %{buildroot}%{_bindir}/xwayland-satellite
install -Dpm0644 xwayland-satellite.man %{buildroot}%{_mandir}/man1/xwayland-satellite.1
install -Dpm0644 resources/xwayland-satellite.service %{buildroot}%{_userunitdir}/xwayland-satellite.service
sed -i 's|^ExecStart=.*|ExecStart=%{_bindir}/xwayland-satellite|' %{buildroot}%{_userunitdir}/xwayland-satellite.service

%files
%license LICENSE
%doc README.md
%{_bindir}/xwayland-satellite
%{_mandir}/man1/xwayland-satellite.1*
%{_userunitdir}/xwayland-satellite.service

%changelog
* Wed Oct 14 2026 c0mpile <16279275+c0mpile@users.noreply.github.com> - 0-0.1
- Automated git snapshot build
