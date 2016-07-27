%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_version: %define python_version %(%{__python} -c "import sys; sys.stdout.write(sys.version[:3])")}

%define rc_version 0

%if 0%{?rc_version}
%define release_prefix 0.rc%{rc_version}.
%endif

Name:       mic
Summary:    Image Creator for Linux Distributions
Version:    0.27.1
Release:    %{?release_prefix}%{?opensuse_bs:<CI_CNT>.<B_CNT>}%{!?opensuse_bs:0}
Group:      Development/Tools
License:    GPLv2
BuildArch:  noarch
URL:        http://www.tizen.org
Source0:    %{name}_%{version}.tar.gz

Requires:   python >= 2.6
Requires:   python-urlgrabber >= 3.9.0
%if 0%{?suse_version} || 0%{?tizen_version:1}
Requires:   python-xml
%endif

%if "%{?python_version}" < "2.7"
Requires:   python-argparse
%endif

%if 0%{?tizen_version:1}
Requires:   python-rpm
%else
Requires:   rpm-python
%endif

Requires:   cpio
# not neccessary
Requires:   gzip
Requires:   bzip2

BuildRequires:  python-devel
%if ! 0%{?tizen_version:1}
BuildRequires:  python-docutils
%endif

Obsoletes:  mic2

BuildRoot:  %{_tmppath}/%{name}_%{version}-build

%description
The tool mic is used to create and manipulate images for Linux distributions.
It is composed of three subcommand\: create, convert, chroot. Subcommand create
is used to create images with different types; subcommand convert is used to
convert an image to a specified type; subcommand chroot is used to chroot into
an image.

%prep
%setup -q -n %{name}-%{version}

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build
make man

%install
rm -rf $RPM_BUILD_ROOT
%if 0%{?suse_version}
%{__python} setup.py install --root=$RPM_BUILD_ROOT --prefix=%{_prefix}
%else
%{__python} setup.py install --root=$RPM_BUILD_ROOT -O1
%endif

# install man page
mkdir -p %{buildroot}/%{_prefix}/share/man/man1
install -m644 doc/mic.1 %{buildroot}/%{_prefix}/share/man/man1

# install bash completion
install -d -m0755 %{buildroot}/%{_sysconfdir}/bash_completion.d/
install -Dp -m0755 etc/bash_completion.d/%{name}.sh %{buildroot}/%{_sysconfdir}/bash_completion.d/

# install zsh completion
install -d -m0755 %{buildroot}/%{_sysconfdir}/zsh_completion.d/
install -Dp -m0755 etc/zsh_completion.d/_%{name} %{buildroot}/%{_sysconfdir}/zsh_completion.d/

%files
%defattr(-,root,root,-)
%doc doc/*
%doc README.rst AUTHORS COPYING ChangeLog
%if ! 0%{?tizen_version:1}
%{_mandir}/man1/*
%endif
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%{python_sitelib}/*
%dir %{_prefix}/lib/%{name}
%{_prefix}/lib/%{name}/*
%{_bindir}/mic
%{_sysconfdir}/bash_completion.d
%{_sysconfdir}/zsh_completion.d

