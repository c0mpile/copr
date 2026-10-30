%global debug_package %{nil}
%global _lto_cflags %{nil}
%global toolchain clang

Name:           gnustep-make
Version:        @VERSION@
Release:        1%{?dist}
Summary:        GNUstep makefile package (libobjc2 / clang flavour)
License:        GPL-3.0-or-later
URL:            https://www.gnustep.org/
Source0:        gnustep-make-%{version}.tar.gz

BuildRequires:  clang
BuildRequires:  libobjc2-devel
BuildRequires:  make
Requires:       gnustep-filesystem = %{version}-%{release}
Requires:       clang
Requires:       libobjc2-devel
Requires:       make

%description
The makefile package is a simple, powerful and extensible way to write
makefiles for a GNUstep-based project. This build is configured for clang and
the GNUstep Objective-C runtime (libobjc2, the non-fragile "ng" ABI), since
EL10 ships no GCC Objective-C compiler.

%package -n gnustep-filesystem
Summary:        The basic directory layout for GNUstep packages
License:        LicenseRef-Not-Copyrightable

%description -n gnustep-filesystem
The basic directory layout for GNUstep packages.

%prep
%autosetup -n gnustep-make-%{version}

sed -i "s|/@libdir@|/%{_lib}|g" FilesystemLayouts/fhs-system
sed -i "s|/@libdir@|/%{_lib}|g" FilesystemLayouts/fhs
# keep everything under /usr/share and /usr/lib64 except the GNUSTEP_LOCAL_* paths
sed -i "s|=/share/GNUstep/Makefiles|=/%{_lib}/GNUstep/Makefiles|" FilesystemLayouts/fhs-system
sed -i "67,77!s|=/local|=|" FilesystemLayouts/fhs-system

%build
export CC=clang CXX=clang++
%configure --with-layout=fhs-system --enable-flattened \
  --with-library-combo=ng-gnu-gnu --enable-objc-nonfragile-abi
%make_build V=1

%install
%make_install GNUSTEP_INSTALLATION_DOMAIN=SYSTEM

for i in Applications WebApplications; do
    mkdir -p %{buildroot}%{_prefix}{,/local}/lib{,64}/GNUstep/$i
done
mkdir -p %{buildroot}%{_prefix}{,/local}/share/GNUstep/Documentation/Developer

%files
%config(noreplace) %{_sysconfdir}/GNUstep/GNUstep.conf
%{_bindir}/gnustep-config
%{_bindir}/gnustep-tests
%{_bindir}/openapp
%{_bindir}/debugapp
%{_bindir}/opentool
%{_libdir}/GNUstep/Makefiles/*
%{_mandir}/man*/*

%files -n gnustep-filesystem
%doc ANNOUNCE FAQ NEWS README
%license COPYING
%dir %{_sysconfdir}/GNUstep
%dir %{_libdir}/GNUstep
%dir %{_libdir}/GNUstep/Makefiles
%dir %{_libdir}/GNUstep/Applications
%dir %{_libdir}/GNUstep/WebApplications
%dir %{_datadir}/GNUstep
%dir %{_datadir}/GNUstep/Documentation
%dir %{_datadir}/GNUstep/Documentation/Developer

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - %{version}-1
- Build for EL10 with clang and libobjc2 (no GCC Objective-C compiler on EL10)
