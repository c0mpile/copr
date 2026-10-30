%global toolchain clang

Name:           gnustep-base
Version:        @VERSION@
Release:        1%{?dist}
Summary:        GNUstep Base library package (libobjc2 / clang flavour)
License:        GPL-3.0-or-later AND LGPL-2.0-or-later
URL:            https://www.gnustep.org/
Source0:        gnustep-base-%{version}.tar.gz

BuildRequires:  clang
BuildRequires:  libobjc2-devel
BuildRequires:  gnustep-make >= 2.9.2
BuildRequires:  libffi-devel >= 3.0.9
BuildRequires:  gnutls-devel
BuildRequires:  libxml2-devel
BuildRequires:  libxslt-devel
BuildRequires:  avahi-compat-libdns_sd-devel
BuildRequires:  gmp-devel
BuildRequires:  libicu-devel
BuildRequires:  libcurl-devel
BuildRequires:  libdispatch-devel
BuildRequires:  pkgconfig
BuildRequires:  make

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       make

%description
The GNUstep Base Library is a fast library of general-purpose, non-graphical
Objective-C classes inspired by the OpenStep API, with Apple and GNU additions.
This build uses clang and the GNUstep Objective-C runtime (libobjc2).

%package libs
Summary:        GNUstep Base run-time libraries
Requires:       gnustep-make%{?_isa} >= 2.9.2

%description libs
Run-time libraries for %{name}.

%package devel
Summary:        Headers of the GNUstep Base library
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       gnustep-make%{?_isa} >= 2.9.2
Requires:       libobjc2-devel%{?_isa}

%description devel
Header files of the GNUstep Base library.

%prep
%autosetup -n gnustep-base-%{version}

%build
export CC="clang -fobjc-runtime=gnustep-2.2 -fblocks -Wno-incompatible-pointer-types" CXX=clang++
ffi_include=$(pkg-config --cflags-only-I libffi | sed -e 's/^\-\I//')
export LDFLAGS="%{__global_ldflags}"
export LIBS="-lobjc"
%configure --with-installation-domain=SYSTEM --disable-ffcall --with-ffi-include="$ffi_include"
%make_build messages=yes GNUSTEP_MAKEFILES=%{_libdir}/GNUstep/Makefiles

%install
%make_install messages=yes GNUSTEP_INSTALLATION_DOMAIN=SYSTEM GNUSTEP_MAKEFILES=%{_libdir}/GNUstep/Makefiles
# Rename pl to pllist to fix the naming conflict
mv %{buildroot}%{_bindir}/pl %{buildroot}%{_bindir}/pllist

%files
%{_bindir}/*
%{_mandir}/man1/*
%{_mandir}/man8/*
%{_libdir}/GNUstep/DTDs/

%files libs
%doc ANNOUNCE NEWS README*
%license COPYING.LIB COPYINGv3
%{_libdir}/GNUstep/Libraries/
%{_libdir}/libgnustep-base.so.*
%{_libdir}/GNUstep/Tools/

%files devel
%{_includedir}/Foundation/
%{_includedir}/CoreFoundation/
%{_includedir}/GNUstepBase/
%{_libdir}/libgnustep-base.so
%{_libdir}/pkgconfig/gnustep-base.pc
%{_libdir}/GNUstep/Makefiles/Additional/base.make

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - %{version}-1
- Build for EL10 with clang and libobjc2, without documentation
