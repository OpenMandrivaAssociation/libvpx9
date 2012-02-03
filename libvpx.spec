Name:		libvpx
Summary:	VP8 Video Codec SDK
Version:	0.9.7
Release:	%mkrel 3
License:	BSD
Group:		System/Libraries
Source0:	http://webm.googlecode.com/files/%{name}-v%{version}-p1.tar.bz2
# Thanks to debian.
Source2:	libvpx.ver
Patch0:		libvpx-0.9.7-no-explicit-dep-on-static-lib.patch
URL:		http://www.webmproject.org/tools/vp8-sdk/
%ifarch %{ix86} x86_64
BuildRequires:	yasm
%endif
BuildRequires:	doxygen php-cli

%description
libvpx provides the VP8 SDK, which allows you to integrate your applications 
with the VP8 video codec, a high quality, royalty free, open source codec 
deployed on millions of computers and devices worldwide. 

%define	major	0
%define	libname	%mklibname vpx %major
%package -n	%{libname}
Summary:	VP8 Video Codec SDK
Group:		System/Libraries

%description -n %{libname}
libvpx provides the VP8 SDK, which allows you to integrate your applications 
with the VP8 video codec, a high quality, royalty free, open source codec 
deployed on millions of computers and devices worldwide. 

%define	devname	%mklibname -d vpx
%package -n	%{devname}
Summary:	Development files for libvpx
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
Development libraries and headers for developing software against 
libvpx.

%package	utils
Summary:	VP8 utilities and tools
Group:		Video

%description	utils
A selection of utilities and tools for VP8, including a sample encoder
and decoder.

%prep
%setup -q -n %{name}-v%{version}-p1
%patch0 -p1 -b .no-static-lib

%build
%ifarch %{ix86}
%global vpxtarget x86-linux-gcc
%else
%ifarch	x86_64
%global	vpxtarget x86_64-linux-gcc
%else
%global vpxtarget generic-gnu
%endif
%endif
%setup_compile_flags

./configure --target=%{vpxtarget} --enable-pic --disable-install-srcs

%make verbose=true target=libs

# Really? You couldn't make this a shared library? Ugh.
# Oh well, I'll do it for you.
mkdir -p tmp
cd tmp
ar x ../libvpx_g.a
cd ..
gcc -fPIC -shared -pthread -lm %{ldflags} -Wl,-soname,libvpx.so.0 -Wl,--version-script,%{SOURCE2} -Wl,-z,noexecstack -o libvpx.so.0.0.0 tmp/*.o 
rm -rf tmp

# Temporarily dance the static libs out of the way
mv libvpx.a libNOTvpx.a
mv libvpx_g.a libNOTvpx_g.a

# We need to do this so the examples can link against it.
ln -sf libvpx.so.0.0.0 libvpx.so

%make verbose=true target=examples
%make verbose=true target=docs

# Put them back so the install doesn't fail
mv libNOTvpx.a libvpx.a
mv libNOTvpx_g.a libvpx_g.a

%install
make DIST_DIR=%{buildroot}%{_prefix} install

cp simple_decoder %{buildroot}%{_bindir}/vp8_simple_decoder                        
cp simple_encoder %{buildroot}%{_bindir}/vp8_simple_encoder                        
cp twopass_encoder %{buildroot}%{_bindir}/vp8_twopass_encoder            

%if %{_lib} != lib
mkdir -p %{buildroot}%{_libdir}
mv %{buildroot}%{_prefix}/lib/pkgconfig %{buildroot}%{_libdir}
%endif

# Fill in the variables
sed -i "s|/usr/local|%{_prefix}|g" %{buildroot}%{_libdir}/pkgconfig/vpx.pc
sed -i "s|\${prefix}/lib|%{_libdir}|g" %{buildroot}%{_libdir}/pkgconfig/vpx.pc

mkdir -p %{buildroot}%{_includedir}/vpx/
install -p libvpx.so.0.0.0 %{buildroot}%{_libdir}
pushd %{buildroot}%{_libdir}
ln -sf libvpx.so.0.0.0 libvpx.so
ln -sf libvpx.so.0.0.0 libvpx.so.0
ln -sf libvpx.so.0.0.0 libvpx.so.0.0
popd
pushd %{buildroot}
# Stuff we don't need.
rm -rf usr/build/ usr/md5sums.txt usr/lib*/*.a usr/CHANGELOG usr/README
# Fix the binary permissions
chmod 755 usr/bin/*
popd

%files -n %{libname}
%doc AUTHORS CHANGELOG LICENSE README
%{_libdir}/libvpx.so.%{major}*

%files -n %{devname}
# These are SDK docs, not really useful to an end-user.
%doc docs/html
%{_includedir}/vpx/
%{_libdir}/pkgconfig/vpx.pc
%{_libdir}/libvpx.so

%files utils
%{_bindir}/*
