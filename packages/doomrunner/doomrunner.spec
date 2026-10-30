%global commit @COMMIT@
%global up doomrunner
%global appid io.github.Youda008.DoomRunner

Name:           doomrunner
Version:        @VERSION@
Release:        1%{?dist}
Summary:        Preset-oriented graphical launcher for Doom source ports
License:        GPL-3.0-only
URL:            https://github.com/Youda008/DoomRunner
# Tarball of the upstream release tag, produced by scripts/make-srpm.sh
Source0:        %{up}-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  qt6-qtbase-devel
BuildRequires:  pkgconfig(minizip)

%description
Doom Runner is a graphical launcher for common Doom source ports (GZDoom,
UZDoom, Zandronum, Crispy Doom, PrBoom+ and others). It is designed around
presets for multi-file modifications, allowing one-click switching between
them. Release build.

%prep
# autofix test: intentional failure
test -e /nonexistent-autofix-test-file
%autosetup -n %{up}-%{commit}

%build
%{qmake_qt6} DoomRunner.pro CONFIG+=release INSTALL_DIR=%{_bindir}
%make_build

%install
%make_install INSTALL_ROOT=%{buildroot}

# Desktop entry, icons and AppStream metadata are installed by packagers (Install/README.md).
install -d %{buildroot}%{_datadir}/applications
sed -e 's|^Categories=Game$|Categories=Game;|' Install/XDG/DoomRunner.desktop \
    > %{buildroot}%{_datadir}/applications/%{appid}.desktop
for size in 16 24 32 48 64 128; do
    install -Dpm0644 Install/XDG/DoomRunner.${size}x${size}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/DoomRunner.png
done
install -Dpm0644 Install/XDG/%{appid}.appdata.xml \
    %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml || :

%files
%license LICENSE
%doc README.md changelog.txt
%{_bindir}/DoomRunner
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/DoomRunner.png
%{_metainfodir}/%{appid}.metainfo.xml

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - 1.9.2-1
- Release build tracking the latest upstream tag
