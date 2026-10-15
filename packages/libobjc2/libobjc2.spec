%global toolchain clang

Name:           libobjc2
Version:        @VERSION@
Release:        1%{?dist}
Summary:        GNUstep Objective-C runtime library
License:        GPL-2.0-only
URL:            https://github.com/gnustep/libobjc2
Source0:        libobjc2-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  clang >= 7.0.1
BuildRequires:  libdispatch-devel >= 1.3
BuildRequires:  robin-map-devel

%description
The GNUstep Objective-C runtime is a drop-in replacement for the GCC runtime.
It supports a legacy and a modern ABI. The modern ABI adds non-fragile
instance variables, protocol uniquing, blocks, declared property
introspection, synthesised property accessors, @synchronized and the
associated reference APIs.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
This package contains development files for %{name}.

%prep
%autosetup -n libobjc2-%{version}
# replace bundled robin-map with the system one
mkdir -p third_party/robin-map/include
ln -sfn %{_includedir}/tsl third_party/robin-map/include/tsl
# Use the C++ implicit include dirs for ObjC++ too; the C ones add -isystem /usr/include,
# which breaks libstdc++'s #include_next <stdlib.h>.
sed -i '23s/^if (MINGW)$/if (TRUE)/' CMakeLists.txt
# drop flag conflicting with FORTIFY_SOURCE
sed -e 's/-O0//g' -i CMakeLists.txt

%build
%cmake -DTESTS=OFF -DCMAKE_INSTALL_LIBDIR=%{_lib}
%cmake_build

%install
%cmake_install
# Avoid clashing with the blocks runtime header (https://github.com/gnustep/libobjc2/issues/199)
mv %{buildroot}%{_includedir}/Block.h %{buildroot}%{_includedir}/Block-libobjc.h

%files
%license COPYING
%doc README.md
%{_libdir}/libobjc.so.*

%files devel
%{_includedir}/*.h
%{_includedir}/objc
%{_libdir}/libobjc.so
%{_libdir}/pkgconfig/libobjc.pc
%{_libdir}/cmake/libobjc/

%changelog
* Wed Oct 14 2026 c0mpile <c0mpile@disroot.org> - %{version}-1
- Build for EL10 from the upstream release tarball
