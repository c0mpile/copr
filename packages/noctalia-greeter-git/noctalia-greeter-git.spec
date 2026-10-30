%global commit @COMMIT@
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global stamp @STAMP@

%global up noctalia-greeter
Name:           noctalia-greeter-git
Version:        @VERSION@^%{stamp}git%{shortcommit}
Release:        1%{?dist}
Summary:        greetd login screen matching the Noctalia shell
License:        MIT
URL:            https://github.com/noctalia-dev/noctalia-greeter
Provides:       noctalia-greeter = %{version}-%{release}
Conflicts:      noctalia-greeter
Conflicts:      noctalia-greeter-nightly
Source0:        %{up}-%{commit}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  stb_image_resize2-devel
BuildRequires:  git
# Derived from upstream meson.build at SRPM time (scripts/gen-buildrequires.py)
# @GENERATED_BUILDREQUIRES@
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(cairo)
BuildRequires:  pkgconfig(cairo-ft)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gio-2.0)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gobject-2.0)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libjxl_threads)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(pangoft2)
BuildRequires:  pkgconfig(tomlplusplus)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wlroots-0.20)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  /usr/bin/wayland-scanner
BuildRequires:  systemd-rpm-macros

Requires:       greetd
Requires:       dbus-daemon
Recommends:     polkit
Provides:       noctalia-greeter = %{version}-%{release}
Provides:       bundled(wuffs)
Conflicts:      noctalia-greeter

%description
A minimal login greeter for greetd that matches the look and feel of Noctalia
Shell. Ships its own wlroots-based kiosk compositor.

Point greetd at it in /etc/greetd/config.toml:

  [default_session]
  command = "/usr/bin/noctalia-greeter-session"
  user = "greetd"

%files -f %{_builddir}/%{name}.files
%license LICENSE
%{_licensedir}/%{name}/third_party/
%doc README.md

%prep
%autosetup -n %{up}-%{commit}
sed -i 's/ greeter greeter / greetd greetd /' data/tmpfiles.d/noctalia-greeter.conf

# Upstream tarball has no .git; stamp the commit into the version string
sed -i "s/'unknown'/'%{shortcommit}'/g" meson.build

%build
%meson -Dc_args="%{build_cflags} -Wno-error=switch"
%meson_build

%install
%meson_install
# tmpfiles.d fallback config is not needed
rm -f %{buildroot}%{_tmpfilesdir}/noctalia-greeter.conf
install -d %{buildroot}%{_licensedir}/%{name}/third_party
find third_party -type f \( -name "LICENSE*" -o -name "COPYING*" -o -name "NOTICE*" \) | while read -r file; do
    dest_dir="%{buildroot}%{_licensedir}/%{name}/$(dirname "$file")"
    install -d "$dest_dir"
    install -p -m 0644 "$file" "$dest_dir/"
done

# Package whatever upstream installs, so new files (desktop entries, icons, ...)
# don't fail the build as unpackaged
find %{buildroot} -mindepth 1 \( -type f -o -type l \) ! -path '%{buildroot}%{_licensedir}/*' -printf '/%%P\n' > %{_builddir}/%{name}.files
find %{buildroot}%{_datadir} -type d -path '%{buildroot}%{_datadir}/noctalia*' -printf '%%%%dir %{_datadir}/%%P\n' >> %{_builddir}/%{name}.files

%changelog
%autochangelog
