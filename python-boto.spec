%if 0%{?fedora} > 12 || 0%{?rhel} > 7
%bcond_without python3
%else
%bcond_with python3
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

Summary:        A simple, lightweight interface to Amazon Web Services
Name:           python-%{pkgname}
Version:        2.46.1
Release:        CROC1%{?buildid}%{?dist}
Epoch:          1441065600
License:        MIT
Group:          Development/Languages
URL:            https://github.com/c2devel/boto
Source0:        https://pypi.io/packages/source/b/boto/boto-%{version}.tar.gz

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
%if %{with python3}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
%endif  # with python3

%if %{with unittests}
BuildRequires:  python-httpretty
BuildRequires:  python-mock
BuildRequires:  python-nose
BuildRequires:  python-requests
%if %{with python3}
BuildRequires:  python3-httpretty
BuildRequires:  python3-mock
BuildRequires:  python3-nose
BuildRequires:  python3-requests
%endif  # with python3
%endif  # with unittests

BuildArch:      noarch

Requires:       python-requests
Obsoletes:      python-boto <= 1441065600:2.12.0-CROC8

%description
Boto is a Python package that provides interfaces to Amazon Web Services.
It supports over thirty services, such as S3 (Simple Storage Service),
SQS (Simple Queue Service), and EC2 (Elastic Compute Cloud) via their
REST and Query APIs.  The goal of boto is to support the full breadth
and depth of Amazon Web Services.  In addition, boto provides support
for other public services such as Google Storage in addition to private
cloud systems like Eucalyptus, OpenStack and Open Nebula.


%if %{with python3}
%package -n python3-%{pkgname}
Summary:        A simple, lightweight interface to Amazon Web Services

Requires:       python3-requests


%description -n python3-%{pkgname}
Boto is a Python package that provides interfaces to Amazon Web Services.
It supports over thirty services, such as S3 (Simple Storage Service),
SQS (Simple Queue Service), and EC2 (Elastic Compute Cloud) via their
REST and Query APIs.  The goal of boto is to support the full breadth
and depth of Amazon Web Services.  In addition, boto provides support
for other public services such as Google Storage in addition to private
cloud systems like Eucalyptus, OpenStack and Open Nebula.
%endif  # with python3


%prep
%setup -q -n %pkgname-%version


%build
%{__python2} setup.py build
%if %{with python3}
%{__python3} setup.py build
%endif  # with python3


%install
%{__python2} setup.py install --skip-build --root $RPM_BUILD_ROOT

%if %{with python3}
%{__python3} setup.py install --skip-build --root $RPM_BUILD_ROOT
%endif  # with python3

rm -f $RPM_BUILD_ROOT/%{_bindir}/*


%check
%if %{with unittests}
%{__python2} tests/test.py default
%if %{with python3}
%{__python3} tests/test.py default
%endif  # with python3
%endif  # with unittests


%files
%defattr(-,root,root,-)
%{python2_sitelib}/boto
%{python2_sitelib}/boto-%{version}-*.egg-info
%doc LICENSE README.rst

%if %{with python3}
%files -n python3-%{pkgname}
%defattr(-,root,root,-)
%{python3_sitelib}/boto
%{python3_sitelib}/boto-%{version}-*.egg-info
%doc LICENSE README.rst
%endif  # with python3


%changelog
* Fri Apr 14 2017 Anton Vazhnetsov <dragen15051@gmail.com> - 2.46.1-CROC1
- Update to latest boto - 2.46.1
