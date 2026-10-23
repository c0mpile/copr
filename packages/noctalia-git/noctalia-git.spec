%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

%global up noctalia
Name:           noctalia-git
Version:        @VERSION@^%{stamp}git%{shortcommit}
Release:        1%{?dist}
Summary:        A sleek, customizable desktop shell crafted for Wayland.
License:        MIT
URL:            https://github.com/noctalia-dev/noctalia
Provides:       noctalia = %{version}-%{release}
Conflicts:      noctalia
Conflicts:      noctalia-nightly
Source0:        %{up}-%{commit}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  git
BuildRequires:  desktop-file-utils
# Derived from upstream meson.build at SRPM time (scripts/gen-buildrequires.py)
# @GENERATED_BUILDREQUIRES@
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(jemalloc)
BuildRequires:  pam-devel
BuildRequires:  stb_image_resize2-devel
BuildRequires:  stb_image_write-devel
Provides:       desktop-notification-daemon
Provides:       PolicyKit-authentication-agent
Requires:       hicolor-icon-theme
Requires:       dejavu-sans-fonts
Recommends:     ddcutil
Recommends:     gpu-screen-recorder
Recommends:     power-profiles-daemon

%description
A sleek, customizable desktop shell crafted for Wayland (Noctalia v5).
Git snapshot build.

%files -f %{_builddir}/%{name}.files
%license LICENSE
%{_licensedir}/%{name}/third_party/
%doc README.md

%prep
%autosetup -n %{up}-%{commit}

# Upstream tarball has no .git; stamp the commit into the version string
sed -i "s/'unknown'/'%{shortcommit}'/g" meson.build

%build
%meson --buildtype=release -Dtests=disabled
%meson_build

%install
%meson_install
install -d %{buildroot}%{_licensedir}/%{name}/third_party
find third_party -type f \( -name "LICENSE*" -o -name "COPYING*" -o -name "NOTICE*" \) | while read -r file; do
    dest_dir="%{buildroot}%{_licensedir}/%{name}/$(dirname "$file")"
    install -d "$dest_dir"
    install -p -m 0644 "$file" "$dest_dir/"
done

# Package whatever upstream installs, so new files (desktop entries, icons, ...)
# don't fail the build as unpackaged
find %{buildroot} -mindepth 1 \( -type f -o -type l \) ! -path '%{buildroot}%{_licensedir}/*' -printf '/%%P\n' > %{_builddir}/%{name}.files
find %{buildroot}%{_datadir} -type d -path '%{buildroot}%{_datadir}/noctalia*' -printf '%%dir %{_datadir}/%%P\n' >> %{_builddir}/%{name}.files

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/dev.noctalia.Noctalia*.desktop

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - 0-0.1
- Automated git snapshot build
