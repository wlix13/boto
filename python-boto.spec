%global dist_raw %(%{__grep} -oP "release \\K[0-9]+\\.[0-9]+" /etc/system-release | tr -d ".")

%if 0%{?fedora} > 12 || 0%{?rhel} && 0%{?dist_raw} >= 75
%bcond_without python3
%else
%bcond_with python3
%endif

# centos 7.2 and lower versions don't have %py2_* macros, so define it manually
%if 0%{?rhel} && 0%{?dist_raw} <= 72
%{!?py2_build: %global py2_build %py_build}
%{!?py2_install: %global py2_install %py_install}
%endif


%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif
%if %{with python3}
%{!?__python3: %global __python3 /usr/bin/python3}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif  # with python3

# Unit tests don't work on python 2.6
%if 0%{?el6}
%bcond_with unittests
%else
%bcond_without unittests
%endif

%define pkgname boto
%define buildid @BUILDID@
%global sum AWS authentication for Amazon S3 for the python requests module
%global descr \
Boto is a Python package that provides interfaces to Amazon Web Services.\
It supports over thirty services, such as S3 (Simple Storage Service),\
SQS (Simple Queue Service), and EC2 (Elastic Compute Cloud) via their\
REST and Query APIs.  The goal of boto is to support the full breadth\
and depth of Amazon Web Services.  In addition, boto provides support\
for other public services such as Google Storage in addition to private\
cloud systems like Eucalyptus, OpenStack and Open Nebula.

Summary:        A simple, lightweight interface to Amazon Web Services
Name:           python-%{pkgname}
Version:        2.46.1
Release:        CROC14%{?buildid}%{?dist}
License:        MIT
Group:          Development/Languages
URL:            https://github.com/c2devel/boto
Source0:        https://pypi.io/packages/source/b/boto/boto-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
%if %{with python3}
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python%{python3_pkgversion}-setuptools
%endif  # with python3

%if %{with unittests}
BuildRequires:  python-httpretty
BuildRequires:  python-mock
BuildRequires:  python-nose
BuildRequires:  python-requests
%if %{with python3}
BuildRequires:  python%{python3_pkgversion}-httpretty
BuildRequires:  python%{python3_pkgversion}-mock
BuildRequires:  python%{python3_pkgversion}-nose
BuildRequires:  python%{python3_pkgversion}-requests
%endif  # with python3
%endif  # with unittests

BuildArch:      noarch

%description
%{descr}


%package -n python2-%{pkgname}
Summary:        %{sum}
Requires:       python-requests
%if 0%{?el6}
Requires:       python-ordereddict
%endif
Provides:       python-boto
Obsoletes:      python-boto <= 1441065600:2.46.1-CROC13%{?dist}


%description -n python2-%{pkgname}
%{descr}


%if %{with python3}
%package -n python%{python3_pkgversion}-%{pkgname}
Summary:        A simple, lightweight interface to Amazon Web Services

Requires:       python%{python3_pkgversion}-requests


%description -n python%{python3_pkgversion}-%{pkgname}
%{descr}
%endif  # with python3


%prep
%setup -q -n %pkgname-%version


%build
%{py2_build}
%if %{with python3}
%{py3_build}
%endif  # with python3


%install
%{py2_install}

%if %{with python3}
%{py3_install}
%endif  # with python3

rm -f %buildroot/%{_bindir}/*


%check
%if %{with unittests}
%{__python2} tests/test.py default
%if %{with python3}
%{__python3} tests/test.py default
%endif  # with python3
%endif  # with unittests


%files -n python2-%{pkgname}
%defattr(-,root,root,-)
%{python2_sitelib}/boto
%{python2_sitelib}/boto-%{version}-*.egg-info
%doc LICENSE README.rst

%if %{with python3}
%files -n python%{python3_pkgversion}-%{pkgname}
%defattr(-,root,root,-)
%{python3_sitelib}/boto
%{python3_sitelib}/boto-%{version}-*.egg-info
%doc LICENSE README.rst
%endif  # with python3


%changelog
* Fri Jul 26 2019 Andrey Kulaev <akulaev@croc.ru> - 2.46.1-CROC14
- ec2: methods for changing sg.rule description
- ec2: add 'description' for GroupOrCIDR

* Thu Jun 06 2019 Pavel Kulyov <pkulev@croc.ru> - 2.46.1-CROC13
- ec2: add parser for Network Interface Association
- ec2: add missing Reset/Describe NI methods
- ec2: drop PrivateIps support
- ec2: add private DNS name parsing to NetworkInterface
- ec2: add switch_id to NetworkInterface

* Wed May 22 2019 Nikita Kretov <kretov995@gmail.com> - - 2.46.1-CROC12
- ec2: add get_tariff method
- travis: pin ubuntu dist
- travis: fix auto-build

* Fri Apr 05 2019 Kretov Nikita <kretov995@gmail.com> - - 2.46.1-CROC11
- cw: add new parameters for MetricAlarms
- ec2: Allow Tags deletion by resource ID only

* Thu Feb 28 2019 Nikita Kretov <kretov995@gmail.com> - 2.46.1-CROC10
- ec2: Add 'modify-instance-placemenet' method

* Thu Jan 10 2019 Mikhail Ushanov <gm.mephisto@gmail.com> - 2.46.1-CROC9
- requirements: pin idna version
- ec2: add to VirtualSwitch an optional parameter 'AvailabilityZone'

* Fri Oct 05 2018 Mikhail Ushanov <gm.mephisto@gmail.com> - 2.46.1-CROC8
- requirements: pin pycparser version
- ec2: update PrivateIp according NAPI
- ec2: update ExtNet according Switch and Subnet API

* Tue Aug 07 2018 Mikhail Ushanov <gm.mephisto@gmail.com> - 2.46.1-CROC7
- ec2: add 'cidr_ipv6' in SecurityGroup entity
- ec2: remove group_type
- ec2: add VirtualSwitch and CRD operations on it
- ec2: add switch_ids to instance
- s3: add AccessDenied error processing

* Mon Apr 02 2018 Mikhail Ushanov <gm.mephisto@gmail.com> - 2.46.1-CROC6
- compat: dont use strict requires to ordereddict

* Tue Dec 26 2017 Mikhail Ushanov <gm.mephisto@gmail.com> - 2.46.1-CROC5
- Freeze max versions for paramiko and cryptography
- boto: dont decode bytes string in PY2 when parse error message

* Tue Oct 03 2017 Mikhail Ushanov <gm.mephisto@gmail.com> - 2.46.1-CROC4
- Add address parameter to address allocation
- ec2: remove 'attach_type' from blockdevicemapping
- ec2: remove 'attach_type' argument from attach volume method

* Tue Jun 27 2017 Mikhail Ushanov <gm.mephisto@gmail.com> - 2.46.1-CROC3
- ec2: fix 'AllowReassociation' param according to AWS API
- ec2: fix tests for addresses.associate

* Fri May 26 2017 Mikhail Ushanov <gm.mephisto@gmail.com> - 2.46.1-CROC2
- ec2: preserved blockdevicemapping order
- rpm: added ordereddict requires on legacy platforms

* Fri Apr 14 2017 Anton Vazhnetsov <dragen15051@gmail.com> - 2.46.1-CROC1
- Update to latest boto - 2.46.1
