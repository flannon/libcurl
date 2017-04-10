Summary: A utility for getting files from remote servers (FTP, HTTP, and others)
Name: curl
Version: 7.53.1
Release: 1%{?dist}
License: MIT
Group: Applications/Internet
Source: http://curl.haxx.se/download/%{name}-%{version}.tar.lzma
#Source0: https://github.com/curl/curl/releases/tag/curl-7_53_1
#Source0: https://github.com/curl/curl/archive/curl-7.53.1.tar.gz
Source1: curlbuild.h
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: automake
BuildRequires: groff
BuildRequires: krb5-devel
BuildRequires: libidn-devel

# we want to use libssh2_scp_send64(), which does not appear in older versions
BuildRequires: libssh2-devel >= 1.2.6

BuildRequires: nss-devel
BuildRequires: openldap-devel
BuildRequires: openssh-clients
BuildRequires: openssh-server
BuildRequires: pkgconfig
BuildRequires: stunnel

# valgrind is not available on some architectures, however it's going to be
# used only by the test-suite anyway
%ifnarch s390 s390x
BuildRequires: valgrind
%endif

BuildRequires: zlib-devel
Requires: libcurl = %{version}-%{release}

# require at least the version of libssh2 that we were built against,
# to ensure that we have the necessary symbols available (#525002, #642796)
%global libssh2_version %(pkg-config --modversion libssh2 2>/dev/null || echo 0)

%description
cURL is a tool for getting files from HTTP, FTP, FILE, LDAP, LDAPS,
DICT, TELNET and TFTP servers, using any of the supported protocols.
cURL is designed to work without user interaction or any kind of
interactivity. cURL offers many useful capabilities, like proxy support,
user authentication, FTP upload, HTTP post, and file transfer resume.

%package -n libcurl
Summary: A library for getting files from web servers
Group: Development/Libraries
Requires: libssh2%{?_isa} >= %{libssh2_version}

%description -n libcurl
This package provides a way for applications to use FTP, HTTP, Gopher and
other servers for getting files.

%package -n libcurl-devel
Summary: Files needed for building applications with libcurl
Group: Development/Libraries
Requires: automake
Requires: libcurl = %{version}-%{release}
Requires: libidn-devel
Requires: pkgconfig

Provides: curl-devel = %{version}-%{release}
Obsoletes: curl-devel < %{version}-%{release}

%description -n libcurl-devel
cURL is a tool for getting files from FTP, HTTP, Gopher, Telnet, and
Dict servers, using any of the supported protocols. The libcurl-devel
package includes files needed for developing applications which can
use cURL's capabilities internally.

%prep
%setup -q

# install curlbuild.h
#install -p %{SOURCE3} %{buildroot}%{jetty_home}%{jetty_base}
#install -p %{SOURCE1} %{_topdir}/SOURCES/%{name}-%{version}/lib
# upstream patches (already applied)


## run aclocal since we are going to run automake
aclocal -I m4

## libnih.m4 is badly broken (#669059), we need to work around it (#669048)
sed -e 's|^m4_rename(\[AC_COPYRIGHT\], \[_NIH_AC_COPYRIGHT\])$||' \
    -e 's|^AC_DEFUN(\[AC_COPYRIGHT\],$|AC_DEFUN([NIH_COPYRIGHT],|' \
    -e 's|^\[_NIH_AC_COPYRIGHT(\[\$1\])$|[AC_COPYRIGHT([$1])|' \
    -i aclocal.m4

# run automake as we added lib/md4.c (#606819) and lib/curl_gssapi.c (#719938)
automake

# required by curl-7.19.4-debug.patch and curl-7.21.0-ntlm.patch
autoconf

## replace hard wired port numbers in the test suite
sed -i s/899\\\([0-9]\\\)/%{?__isa_bits}9\\1/ tests/data/test*

## Convert docs to UTF-8
for f in CHANGES README; do
	iconv -f iso-8859-1 -t utf8 < ${f} > ${f}.utf8
	mv -f ${f}.utf8 ${f}
done

## disable test 303 on ppc/ppc64 (it times out occasionally)
%ifarch ppc ppc64
echo "303" >> tests/data/DISABLED
%endif

#%build
#%configure --with-ssl=/usr/include/ssl --disable-shared --with-nss \
#        --enable-ipv6 \
#	--with-ca-bundle=%{_sysconfdir}/pki/tls/certs/ca-bundle.crt \
#	--with-gssapi --with-libidn \
#	--enable-ldaps --with-libssh2 --enable-manual
##sed -i -e 's,-L/usr/lib ,,g;s,-L/usr/lib64 ,,g;s,-L/usr/lib$,,g;s,-L/usr/lib64$,,g' \
##	Makefile libcurl.pc
### Remove bogus rpath
##sed -i \
##	-e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
##	-e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
#
## uncomment to turn off optimizations
##find -name Makefile | xargs sed -i 's/-O2/-O0/'
#
#make %{?_smp_mflags}
#
#%check
#export LD_LIBRARY_PATH=$RPM_BUILD_ROOT%{_libdir}
#cd tests
#make %{?_smp_mflags}
## use different port range for 32bit and 64bit build, thus make it possible
## to run both in parallel on the same machine
#./runtests.pl -a -b%{?__isa_bits}90 -p -v
#
#%install
#rm -rf $RPM_BUILD_ROOT
#
#make DESTDIR=$RPM_BUILD_ROOT INSTALL="%{__install} -p" install
#
#rm -f ${RPM_BUILD_ROOT}%{_libdir}/libcurl.la
#
#install -d $RPM_BUILD_ROOT/%{_datadir}/aclocal
#install -m 644 docs/libcurl/libcurl.m4 $RPM_BUILD_ROOT/%{_datadir}/aclocal
#
### Make libcurl-devel multilib-ready (bug #488922)
##%if 0%{?__isa_bits} == 64
##%define _curlbuild_h curlbuild-64.h
##%else
##%define _curlbuild_h curlbuild-32.h
##%endif
##mv $RPM_BUILD_ROOT%{_includedir}/curl/curlbuild.h \
##   $RPM_BUILD_ROOT%{_includedir}/curl/%{_curlbuild_h}
##
##install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{_includedir}/curl/curlbuild.h
#
### don't need curl's copy of the certs; use openssl's
##find ${RPM_BUILD_ROOT} -name ca-bundle.crt -exec rm -f '{}' \;

#%clean
#rm -rf $RPM_BUILD_ROOT
#
##%post -n libcurl -p /sbin/ldconfig
##
##%postun -n libcurl -p /sbin/ldconfig
#
#%files
#%defattr(-,root,root,-)
#%doc CHANGES README* COPYING
#%doc docs/BUGS docs/FAQ docs/FEATURES
#%doc docs/MANUAL docs/RESOURCES
#%doc docs/TheArtOfHttpScripting docs/TODO
#%{_bindir}/curl
#%{_mandir}/man1/curl.1*
#
#%files -n libcurl
#%defattr(-,root,root,-)
#%{_libdir}/libcurl.so.*
#
#%files -n libcurl-devel
#%defattr(-,root,root,-)
#%doc docs/examples/*.c docs/examples/Makefile.example docs/INTERNALS
#%doc docs/CONTRIBUTE docs/libcurl/ABI
#%{_bindir}/curl-config*
#%{_includedir}/curl
#%{_libdir}/*.so
#%{_libdir}/pkgconfig/*.pc
#%{_mandir}/man1/curl-config.1*
#%{_mandir}/man3/*
#%{_datadir}/aclocal/libcurl.m4
#
#%changelog
#* Sun Mar 09 2017 Flannon Jackson <flannon@nyu.edu> 7.53.1
#- Repurposed specfile from 7.19.7-53
#
