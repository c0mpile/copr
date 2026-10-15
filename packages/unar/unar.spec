%global detectorver 1.1
%global toolchain clang

Name:           unar
Version:        @VERSION@
Release:        1%{?dist}
Summary:        Multi-format extractor
License:        LGPL-2.1-or-later
URL:            https://theunarchiver.com/command-line
Source0:        unar-%{version}.tar.gz
Source1:        universal-detector-%{detectorver}.tar.gz
Patch1:         unar-int-conversion.patch

BuildRequires:  clang
BuildRequires:  gcc-c++
BuildRequires:  libobjc2-devel
BuildRequires:  gnustep-make
BuildRequires:  gnustep-base-devel
BuildRequires:  bzip2-devel
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(wavpack)

%description
The command-line utilities lsar and unar list and extract files in many
archive formats, including RARv5 with encryption and multiple volumes. unar can
serve as a free replacement for unrar. Built for EL10 with clang and the GNUstep
runtime (libobjc2), since EL10 has no GCC Objective-C compiler.

%prep
%setup -q -c
tar -xf %{SOURCE1}
%patch -P1 -p1
mv universal-detector-%{detectorver} UniversalDetector
rm -fr __MACOSX "The Unarchiver"
find . -type f -print0 | xargs -0 chmod -x

%build
%define _lto_cflags %{nil}
objcflags=$(gnustep-config --objc-flags)
make -C XADMaster-%{version} -f Makefile.linux \
  OBJCC=clang CC=clang CXX=clang++ LD=clang++ \
  GNUSTEP_OPTS="$objcflags -fexceptions -fobjc-exceptions" \
  ALL_LDFLAGS="-Wl,--whole-archive -fexceptions -fobjc-runtime=gnustep-2.2 $(gnustep-config --base-libs | tr ' ' '\n' | grep '^-L' | tr '\n' ' ')" \
  OBJCFLAGS="%{optflags}"

%install
pushd XADMaster-%{version}
install -d %{buildroot}%{_bindir}
install -pm755 unar lsar %{buildroot}%{_bindir}
install -d %{buildroot}%{_mandir}/man1
install -pm644 Extra/*.1 %{buildroot}%{_mandir}/man1
install -d %{buildroot}%{_datadir}/bash-completion/completions
install -pm644 Extra/lsar.bash_completion %{buildroot}%{_datadir}/bash-completion/completions/lsar
install -pm644 Extra/unar.bash_completion %{buildroot}%{_datadir}/bash-completion/completions/unar
popd

%files
%license XADMaster-%{version}/LICENSE
%{_bindir}/lsar
%{_bindir}/unar
%{_mandir}/man1/*.1*
%{_datadir}/bash-completion/completions/*

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - %{version}-1
- Build for EL10 with clang and libobjc2, based on the Fedora package
