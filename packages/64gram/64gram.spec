# Repackages upstream's official Linux build. A from-source build of Telegram
# Desktop needs tg_owt, tdlib and many patches and takes hours to compile.
%global debug_package %{nil}
%global __strip /bin/true
%global __os_install_post %{nil}
%global _build_id_links none
%global appid io.github.tdesktop_x64.TDesktop

Name:           64gram
Version:        @VERSION@
Release:        1%{?dist}
Summary:        Unofficial Telegram Desktop client with extra features
License:        GPL-3.0-or-later AND LGPL-3.0-only AND BSD-3-Clause AND MIT AND Apache-2.0
URL:            https://github.com/TDesktop-x64/tdesktop
# Corresponding source: https://github.com/TDesktop-x64/tdesktop/tree/v%%{version}
Source0:        64gram-%{version}-linux.zip
Source1:        LICENSE
Source2:        LEGAL
Source3:        %{appid}.desktop
Source4:        %{appid}.metainfo.xml
Source5:        %{appid}.service
Source10:       icon16.png
Source11:       icon32.png
Source12:       icon48.png
Source13:       icon64.png
Source14:       icon128.png
Source15:       icon256.png
Source16:       icon512.png

ExclusiveArch:  x86_64

BuildRequires:  unzip
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       hicolor-icon-theme
Recommends:     xdg-desktop-portal
Recommends:     webkitgtk6.0

%description
64Gram is an unofficial Telegram Desktop client with extra features. This
package installs the official prebuilt Linux release. Its built-in updater is
disabled; updates come from this repository through dnf.

Source code (GPL-3.0-or-later): https://github.com/TDesktop-x64/tdesktop

%prep
%setup -q -c -T
unzip -q %{SOURCE0}
cp -p %{SOURCE1} %{SOURCE2} .

%build
# nothing to build

%install
install -Dpm0755 Telegram %{buildroot}/opt/64Gram/Telegram
install -Dpm0755 Updater  %{buildroot}/opt/64Gram/Updater

# Tell the app that this install is managed by the package manager: it disables
# its built-in updater when its own path is listed in externalupdater.d.
install -d %{buildroot}/opt/64Gram/externalupdater.d
echo /opt/64Gram/Telegram > %{buildroot}/opt/64Gram/externalupdater.d/64gram

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/64gram <<'LAUNCHER'
#!/bin/sh
exec /opt/64Gram/Telegram "$@"
LAUNCHER
chmod 0755 %{buildroot}%{_bindir}/64gram

# Use our own launcher and a distinct icon name so this can coexist with telegram-desktop.
install -d %{buildroot}%{_datadir}/applications
sed -e 's|^TryExec=.*|TryExec=64gram|' \
    -e 's|^Exec=Telegram -quit|Exec=64gram -quit|' \
    -e 's|^Exec=Telegram|Exec=64gram|' \
    -e 's|^Icon=org.telegram.desktop|Icon=64gram|' \
    %{SOURCE3} > %{buildroot}%{_datadir}/applications/%{appid}.desktop

install -d %{buildroot}%{_datadir}/dbus-1/services
sed 's|^Exec=.*|Exec=%{_bindir}/64gram|' %{SOURCE5} \
    > %{buildroot}%{_datadir}/dbus-1/services/%{appid}.service

install -Dpm0644 %{SOURCE4} %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

for size in 16 32 48 64 128 256 512; do
    install -Dpm0644 %{_sourcedir}/icon${size}.png \
        %{buildroot}%{_datadir}/icons/hicolor/${size}x${size}/apps/64gram.png
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml || :

%files
%license LICENSE LEGAL
/opt/64Gram/
%{_bindir}/64gram
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/dbus-1/services/%{appid}.service
%{_metainfodir}/%{appid}.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/64gram.png

%changelog
* Wed Oct 14 2026 c0mpile <16279275+c0mpile@users.noreply.github.com> - 1.2.10-1
- Repackage the upstream Linux release
