Name: heat
Summary: This software provides AWS CloudFormation functionality for OpenStack
Version: 7
Release: 3git26022013%{?dist}
License: ASL 2.0
Group: System Environment/Base
URL: http://heat-api.org
Source0: https://github.com/downloads/heat-api/heat/heat-%{version}.tar.gz
Source1: heat.logrotate
Source2: openstack-heat-api
Source3: openstack-heat-api-cfn
Source4: openstack-heat-cloudwatch
Source5: openstack-heat-engine

Patch0: switch-to-using-m2crypto.patch
Patch1: el6.patch

BuildArch: noarch
BuildRequires: python2-devel
BuildRequires: python-setuptools

Requires: python-eventlet
Requires: python-glanceclient
Requires: python-greenlet
Requires: python-httplib2
Requires: python-iso8601
Requires: python-keystoneclient
Requires: python-kombu
Requires: python-lxml
Requires: python-memcached
Requires: python-migrate
Requires: python-novaclient
Requires: python-paste
Requires: python-qpid
Requires: pysendfile
Requires: python-webob
Requires: m2crypto

Requires: python-paste-deploy1.5
Requires: python-routes1.12
Requires: python-sqlalchemy0.7

Requires: python-oslo-config
Requires: python-anyjson

Requires(pre): shadow-utils

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
export OSLO_PACKAGE_VERSION=%{version}
%{__python} setup.py build

%install
export OSLO_PACKAGE_VERSION=%{version}
%{__python} setup.py install -O1 --skip-build --root=%{buildroot}
sed -i -e '/^#!/,1 d' %{buildroot}/%{python_sitelib}/heat/db/sqlalchemy/manage.py
sed -i -e '/^#!/,1 d' %{buildroot}/%{python_sitelib}/heat/db/sqlalchemy/migrate_repo/manage.py
sed -i -e '/^#!/,1 d' %{buildroot}/%{python_sitelib}/heat/testing/runner.py
mkdir -p %{buildroot}/var/log/heat/
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/heat



# install init scripts
install -p -D -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/openstack-%{name}-api
install -p -D -m 755 %{SOURCE3} %{buildroot}%{_initrddir}/openstack-%{name}-api-cfn
install -p -D -m 755 %{SOURCE4} %{buildroot}%{_initrddir}/openstack-%{name}-cloudwatch
install -p -D -m 755 %{SOURCE5} %{buildroot}%{_initrddir}/openstack-%{name}-engine

# install pid dir
install -d -m 755 %{buildroot}%{_localstatedir}/run/heat/

mkdir -p %{buildroot}/var/lib/heat/
mkdir -p %{buildroot}/etc/heat/
#mkdir -p %{buildroot}/%{_mandir}/man1/
#cp -v docs/man/man1/* %{buildroot}/%{_mandir}/man1/
rm -rf %{buildroot}/var/lib/heat/.dummy

install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/heat/heat-api.conf %{buildroot}/%{_sysconfdir}/heat
install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/heat/heat-api-paste.ini %{buildroot}/%{_sysconfdir}/heat
install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/heat/heat-api-cfn.conf %{buildroot}/%{_sysconfdir}/heat
install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/heat/heat-api-cfn-paste.ini %{buildroot}/%{_sysconfdir}/heat
install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/heat/heat-api-cloudwatch.conf %{buildroot}/%{_sysconfdir}/heat
install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/heat/heat-api-cloudwatch-paste.ini %{buildroot}/%{_sysconfdir}/heat
install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/heat/heat-engine.conf %{buildroot}/%{_sysconfdir}/heat
install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/boto.cfg %{buildroot}/%{_sysconfdir}/heat
install -p -D -m 644 %{_builddir}/%{name}-%{version}/etc/bash_completion.d/heat-cfn %{buildroot}/%{_sysconfdir}/bash_completion.d/heat-cfn

%description
Heat provides AWS CloudFormation and CloudWatch functionality for OpenStack.

%files
%doc README.rst LICENSE
#%{_mandir}/man1/*.gz
%{_bindir}/*
%{python_sitelib}/heat*
%dir %attr(0755,openstack-heat,root) %{_localstatedir}/log/heat
%dir %attr(0755,openstack-heat,root) %{_localstatedir}/lib/heat
%dir %{_initrddir}/openstack-%{name}-*
%dir %attr(0755, openstack-heat, openstack-heat) %{_localstatedir}/run/heat
%dir %{_sysconfdir}/heat
%config(noreplace) %{_sysconfdir}/logrotate.d/heat
%config(noreplace) %{_sysconfdir}/bash_completion.d/heat-cfn
%config(noreplace) %attr(-,root,openstack-heat) %{_sysconfdir}/heat/heat-api.conf
%config(noreplace) %attr(-,root,openstack-heat) %{_sysconfdir}/heat/heat-api-paste.ini
%config(noreplace) %attr(-,root,openstack-heat) %{_sysconfdir}/heat/heat-api-cfn.conf
%config(noreplace) %attr(-,root,openstack-heat) %{_sysconfdir}/heat/heat-api-cfn-paste.ini
%config(noreplace) %attr(-,root,openstack-heat) %{_sysconfdir}/heat/heat-api-cloudwatch.conf
%config(noreplace) %attr(-,root,openstack-heat) %{_sysconfdir}/heat/heat-api-cloudwatch-paste.ini
%config(noreplace) %attr(-,root,openstack-heat) %{_sysconfdir}/heat/heat-engine.conf
%config(noreplace) %attr(-,root,openstack-heat) %{_sysconfdir}/heat/boto.cfg

%pre
getent group openstack-heat >/dev/null || groupadd -r openstack-heat --gid 187
getent passwd openstack-heat  >/dev/null || \
useradd -u 187 -r -g openstack-heat -d %{_localstatedir}/lib/heat -s /sbin/nologin \
    -c "OpenStack Heat Daemon" openstack-heat
exit 0

%post
comps="api"
for comp in $comps; do
    /sbin/chkconfig --add openstack-heat-${comp}
done

%preun
if [ $1 = 0 ] ; then
    comps="api"
    for comp in $comps; do
        /sbin/service openstack-heat-${comp} stop >/dev/null 2>&1
        /sbin/chkconfig --del openstack-heat-${comp}
    done
fi

%postun
if [ "$1" -ge "1" ] ; then
    comps="api"
    for comp in $comps; do
        /sbin/service openstack-heat-${comp} condrestart >/dev/null 2>&1 || :
    done
fi

%changelog
* Mon Feb 26 2013 Robert van Leeuwen <robert.vanleeuwen@spilgames.com> 7-3git26022013
- Re-added updated crypto patch
- Added required versions of packages

* Mon Feb 26 2013 Robert van Leeuwen <robert.vanleeuwen@spilgames.com> 7-3git26022013
- New master branch import
- Added patch to fix module versions

* Mon Feb 25 2013 Robert van Leeuwen <robert.vanleeuwen@spilgames.com> 7-3git25022013
- Switched to using master branch
- Removed patch for Rabbit Support, patch is merged with main.
- Removed crypto patch, patch is broken for current master branch. Testing with updated crypto library

* Mon Feb 25 2013 Robert van Leeuwen <robert.vanleeuwen@spilgames.com> 7-2.1
- Added patch to fix Rabbit support

* Fri Feb 22 2013 Robert van Leeuwen <robert.vanleeuwen@spilgames.com> 7-2
- Update to 7.2

* Fri Feb 15 2013 Robert van Leeuwen <robert.vanleeuwen@spilgames.com> 7-1
- Import from fedora, modified for SL6

* Fri Oct 26 2012 Zane Bitter <zbitter@redhat.com> 7-1
- rebase to v7
- add heat-api daemon (OpenStack-native API)

* Wed Sep 26 2012 Steven Dake <sdake@redhat.com> 6-6
- Merge upstream commit 5208008db047d8cda231100db817c6f0e1c190a5
- Resolves: RHBZ#860105
- fix "heat-keystone-setup not available in heat rpm"

* Wed Sep 26 2012 Steven Dake <sdake@redhat.com> 6-5
- Merge upstream commit d9f63269f1a0205811cd84487787c8c1291a952b
- Resolves: RHBZ#860726
- fix "heat cli prints warning on each operation"

* Wed Sep 26 2012 Jeff Peeler <jpeeler@redhat.com> 6-4
- switch requires to python-glanceclient

* Tue Sep 25 2012 Jeff Peeler <jpeeler@redhat.com> 6-3
- change systemd scripts to use openstack-heat user

* Fri Sep 21 2012 Jeff Peeler <jpeeler@redhat.com> 6-2
- update m2crypto patch (Fedora)
- fix user/group install permissions

* Tue Sep 18 2012 Steven Dake <sdake@redhat.com> 6-1
- update to new v6 binary names in heat

* Tue Aug 21 2012 Jeff Peeler <jpeeler@redhat.com> 5-5
- updated systemd scriptlets

* Tue Aug  7 2012 Jeff Peeler <jpeeler@redhat.com> 5-4
- make UID/GID more specific as openstack-heat

* Tue Aug  7 2012 Jeff Peeler <jpeeler@redhat.com> 5-3
- assign specific UID/GID for use with Heat account (845078)

* Wed Aug 2 2012 Jeff Peeler <jpeeler@redhat.com> 5-2
- create heat user and change file permissions
- set systemd scripts to run as heat user

* Fri Jul 27 2012 Ian Main <imain@redhat.com> - 5-1
- added m2crypto patch.
- bumped version for new release.
- added boto.cfg to sysconfigdir

* Tue Jul 24 2012 Jeff Peeler <jpeeler@redhat.com> - 4-5
- added LICENSE to docs
- added dist tag
- added heat directory to files section
- removed unnecessary defattr

* Tue Jul 24 2012 Jeff Peeler <jpeeler@redhat.com> - 4-4
- remove pycrypto requires

* Fri Jul 20 2012 Jeff Peeler <jpeeler@redhat.com> - 4-3
- change python-devel to python2-devel

* Wed Jul 11 2012 Jeff Peeler <jpeeler@redhat.com> - 4-2
- add necessary requires
- removed shebang line for scripts not requiring executable permissions
- add logrotate, removes all rpmlint warnings except for python-httplib2
- remove buildroot tag since everything since F10 has a default buildroot
- remove clean section as it is not required as of F13
- add systemd unit files
- change source URL to download location which doesn't require a SHA

* Fri Jun 8 2012 Steven Dake <sdake@redhat.com> - 4-1
- removed jeos from packaging since that comes from another repository
- compressed all separate packages into one package
- removed setup options which were producing incorrect results
- replaced python with {__python}
- added a br on python-devel
- added a --skip-build to the install step
- added percent-dir for directories
- fixed most rpmlint warnings/errors

* Mon Apr 16 2012 Chris Alfonso <calfonso@redhat.com> - 3-1
- initial openstack package log

