# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.22
# 
# >> macros
# << macros

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
Name:       mic
Summary:    Image Creator for Linux Distributions
Version:    0.3
Release:    1
Group:      System/Base
License:    GPLv2
BuildArch:  noarch
URL:        http://www.tizen.org
Source0:    %{name}-%{version}.tar.gz
Source100:  mic.yaml
Requires:   util-linux
Requires:   coreutils
Requires:   python >= 2.5
Requires:   e2fsprogs
Requires:   dosfstools >= 2.11-8
Requires:   yum >= 3.2.24
Requires:   syslinux >= 3.82
Requires:   python-urlgrabber
Requires:   kpartx
Requires:   parted
Requires:   device-mapper
Requires:   /usr/bin/mkisofs
Requires:   cpio
Requires:   isomd5sum
Requires:   gzip
Requires:   bzip2
Requires:   squashfs-tools >= 4.0
%if 0%{?suse_version}
Requires:   btrfsprogs
%else
Requires:   btrfs-progs
%endif
Requires:   python-zypp >= 0.5.7
BuildRequires:  python-devel
BuildRoot:  %{_tmppath}/%{name}-%{version}-build


%description
The tool mic is used to create and manipulate images for Linux distributions.
It is composed of three subcommand\: create, convert, chroot. Subcommand create
is used to create images with different types; subcommand convert is used to
convert an image to a specified type; subcommand chroot is used to chroot into
an image.




%prep
%setup -q -n %{name}-%{version}

# >> setup
# << setup

%build
# >> build pre
# << build pre

CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

# >> build post
# << build post
%install
rm -rf $RPM_BUILD_ROOT
# >> install pre
# << install pre
%if 0%{?suse_version}
%{__python} setup.py install --root=$RPM_BUILD_ROOT --prefix=%{_prefix}
%else
%{__python} setup.py install --root=$RPM_BUILD_ROOT -O1
%endif

# >> install post
# install man page
mkdir -p %{buildroot}/%{_prefix}/share/man/man1
install -m644 doc/mic.1 %{buildroot}/%{_prefix}/share/man/man1
# << install post






%files
%defattr(-,root,root,-)
# >> files
%doc README.rst
%{_mandir}/man1/*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{python_sitelib}/*
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/*
%{_bindir}/*
# << files

