%global commit @COMMIT@
%global up uzdoom
%define debug_package %{nil}

Name:           uzdoom
Version:        @VERSION@
Release:        1%{?dist}
Summary:        An OpenGL DOOM source port with graphic and modding extensions
License:        GPL-3.0-only
URL:            https://github.com/UZDoom/uzdoom
# Tarball of the upstream release tag, produced by scripts/make-srpm.sh
Source0:        %{up}-%{commit}.tar.gz

Provides:       zdoom = 2.8.1
Provides:       qzdoom = 1.3.0
Provides:       gzdoom = %{version}
Provides:       bundled(re2c) = 0.16.0
Provides:       bundled(gdtoa)
Provides:       bundled(zmusic)

Patch1:         %{name}-waddir.patch
Patch2:         %{name}-asmjit.patch

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  cmake
BuildRequires:  tar
BuildRequires:  git
BuildRequires:  nasm
BuildRequires:  glew-devel
BuildRequires:  timidity++
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(flac)
BuildRequires:  pkgconfig(bzip2)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(liblzma)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(fluidsynth)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(sdl)
BuildRequires:  pkgconfig(sdl2)
BuildRequires:  pkgconfig(sndfile)
BuildRequires:  pkgconfig(libgme)
BuildRequires:  pkgconfig(openal)
BuildRequires:  pkgconfig(libmpg123)
BuildRequires:  pkgconfig(vulkan)
BuildRequires:  pkgconfig(vpx)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(wildmidi)

Requires:       wildmidi
Requires:       openal-soft
Requires:       fluidsynth
Requires:       SDL2
Recommends:     freedoom

%description
UZDoom is a feature-rich OpenGL and Vulkan DOOM source port derived from the
ZDoom family of engines. It runs Doom, Doom II, Heretic, Hexen, Strife and other
Doom engine games, with support for modern resolutions, mouselook, jumping and
crouching, colored lighting, 3D floors, extensive modding via ACS and ZScript,
and multiplayer. Release build.

%prep
%autosetup -n %{up}-%{commit} -p1

%build
%define _lto_cflags %nil
export _rhel_flags="-fPIC"
# set build version
export GIT_DESCRIBE="%{version}"

%cmake  -DNO_STRIP=1 \
        -DCMAKE_C_FLAGS="$_rhel_flags" -DCMAKE_CXX_FLAGS="$_rhel_flags" \
        -DCMAKE_SHARED_LINKER_FLAGS="" \
        -DCMAKE_EXE_LINKER_FLAGS="" \
        -DCMAKE_MODULE_LINKER_FLAGS="" \
        -DBUILD_SHARED_LIBS="OFF" \
        -DINSTALL_DOCS_PATH="%{_docdir}/%{name}" \
        -DINSTALL_PK3_PATH="%{_datadir}/doom" \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo
%cmake_build

%install
%cmake_install

mkdir -p %{buildroot}%{_datadir}/applications

# Fallback soundfont and FM banks: symlink into the doom data dir
pushd %{buildroot}%{_datadir}/doom
    ln -s %{_datadir}/games/uzdoom/soundfonts soundfonts
    ln -s %{_datadir}/games/uzdoom/fm_banks fm_banks
popd

%post
echo "INFO: %{name}: The global IWAD directory is %{_datadir}/doom."
echo "INFO: %{name}: If you are upgrading from gzdoom, please see the following:"
echo "INFO: %{name}:   https://forum.zdoom.org/viewtopic.php?t=81099"

%files
%doc docs/console.css docs/console.html docs/licenses/*
%{_bindir}/%{name}
%{_datadir}/doom/*
%{_docdir}/%{name}/*
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/scalable/apps/*.svg
%{_datadir}/metainfo/*.xml
%{_datadir}/mime/packages/*.xml
%{_datadir}/games/uzdoom/*

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - 5.0.3-1
- Release build tracking the latest upstream tag
