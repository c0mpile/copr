# Repackages upstream's official release .deb (electron-builder output). Building
# the Electron app from source needs Node, Bun, Rust and network access, which
# the Copr build environment does not allow.
%global debug_package %{nil}
%global __strip /bin/true
%global __os_install_post %{nil}
%global __arch_install_post %{nil}
%global _build_id_links none
%global _missing_build_ids_terminate_build 0
%global _binary_payload w12T.zstdio

# Bundled Chromium/Electron libraries must not become system provides/requires.
AutoReqProv:    no

Name:           voicestudio
Version:        @VERSION@
Release:        2%{?dist}
Summary:        Local voice cloning, voice design, dubbing and transcription desktop app
License:        AGPL-3.0-only AND MIT AND BSD-3-Clause
URL:            https://github.com/debpalash/VoiceStudio
# Corresponding source (AGPL-3.0): https://github.com/debpalash/VoiceStudio/tree/v%%{version}
Source0:        voicestudio-electron-%{version}-linux-x64.deb

ExclusiveArch:  x86_64

BuildRequires:  binutils
BuildRequires:  tar
BuildRequires:  xz
BuildRequires:  zstd
BuildRequires:  gzip
BuildRequires:  desktop-file-utils

Requires:       gtk3
Requires:       libnotify
Requires:       nss
Requires:       libXScrnSaver
Requires:       libXtst
Requires:       xdg-utils
Requires:       at-spi2-core
Requires:       libsecret
Requires:       libuuid
Requires:       alsa-lib
Requires:       cups-libs
Requires:       libdrm
Requires:       mesa-libgbm
Requires:       libxkbcommon
Requires:       libXrandr
Requires:       libXcomposite
Requires:       libXdamage
Requires:       hicolor-icon-theme
Recommends:     libappindicator-gtk3
Recommends:     ffmpeg-free

%description
VoiceStudio is an open-source, fully local voice toolkit: voice cloning, voice
design, video dubbing, dictation, transcription and audiobook creation in
hundreds of languages.

This package installs the official Electron desktop app from the upstream
release. The Python backend and speech models are downloaded by the app itself
on first use. The in-app updater is disabled; updates come from this repository
through dnf.

Source code (AGPL-3.0): https://github.com/debpalash/VoiceStudio

%prep
%setup -q -c -T
deb=%{SOURCE0}
member=$(ar t "$deb" | grep '^data\.tar')
case $member in
  *.xz)  unc="xz -dc" ;;
  *.zst) unc="zstd -dc" ;;
  *.gz)  unc="gzip -dc" ;;
  *)     unc="cat" ;;
esac
ar p "$deb" "$member" | $unc | tar -x --no-same-owner

%build
# nothing to build

%install
mkdir -p %{buildroot}/opt
cp -a opt/VoiceStudio %{buildroot}/opt/VoiceStudio

# Use user namespaces for the Chromium sandbox rather than a setuid helper.
chmod 0755 %{buildroot}/opt/VoiceStudio/chrome-sandbox

# The app's AppArmor profile is for Debian/Ubuntu; Fedora uses SELinux.
rm -f %{buildroot}/opt/VoiceStudio/resources/apparmor-profile

# Launcher: package-managed installs update through dnf, not the in-app updater.
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/voicestudio-electron <<'LAUNCHER'
#!/bin/sh
export VOICESTUDIO_DISABLE_UPDATER=1
# Fedora's uv config disables Python downloads, but the app sets up its own managed Python 3.11.
export UV_PYTHON_DOWNLOADS=automatic
exec /opt/VoiceStudio/voicestudio-electron "$@"
LAUNCHER
chmod 0755 %{buildroot}%{_bindir}/voicestudio-electron

install -Dpm0644 usr/share/icons/hicolor/512x512/apps/voicestudio-electron.png \
    %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/voicestudio-electron.png

install -d %{buildroot}%{_datadir}/applications
sed -e 's|^Exec=.*|Exec=voicestudio-electron %U|' \
    -e 's|^Categories=.*|Categories=AudioVideo;Audio;|' \
    usr/share/applications/VoiceStudio.desktop \
    > %{buildroot}%{_datadir}/applications/VoiceStudio.desktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/VoiceStudio.desktop || true

%files
%license /opt/VoiceStudio/LICENSE.electron.txt
%license /opt/VoiceStudio/LICENSES.chromium.html
%license /opt/VoiceStudio/resources/LICENSE
/opt/VoiceStudio/
%{_bindir}/voicestudio-electron
%{_datadir}/applications/VoiceStudio.desktop
%{_datadir}/icons/hicolor/512x512/apps/voicestudio-electron.png

%changelog
* Thu Oct 15 2026 c0mpile <c0mpile@disroot.org> - 0.5.6-2
- Allow uv to download its managed Python; Fedora's uv config disables that and the first-run setup failed

* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - 0.5.6-1
- Repackage the upstream release .deb
