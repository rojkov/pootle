#
# spec file for package pootle
#
# Copyright (c) 2010 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%define us_name pootle
%define varlib %{_var}/lib
%define apxs %{_sbindir}/apxs2
%define ap_sysconfdir %(%{apxs} -q SYSCONFDIR)
%define ap_libexecdir %(%{apxs} -q LIBEXECDIR)
%if 0%{?suse_version}
%define ap_usr wwwrun
%define ap_grp www
%else
%define ap_usr nobody
%define ap_grp nogroup
%endif

Name:		pootle
Version:	2.4.99.1
Release:	1
Summary:	An online collaborative localization tool

Group:		Development/Tools/Other
License:	GPLv2
URL:		http://translate.sourceforge.net/wiki/pootle/index
Source0:	%{us_name}-%{version}.tar.bz2
Source1:	localsettings.conf
Source2:	%{name}.conf
Source3:	%{name}.conf.vhost
Source4:	README.suse
Source5:    wsgi.py
Source6:	%{name}-ssl.conf.vhost
Patch0:     0001-switch-docs-to-default-theme.patch
Patch1:     0002-disable-strict-checking-of-LDAP-SSL-cerificate.patch
Patch2:     0003-Add-middleware-for-basic-auth.patch
Patch3:     0004-Always-show-summary-area.patch
Patch4:     0005-plug-in-gitapi-if-present.patch
Patch5:     0006-plug-in-jollaapi-if-present.patch
BuildRoot:	%{_tmppath}/%{name}-%{version}-build

BuildArch:	noarch
BuildRequires:  apache2-devel
BuildRequires:  python-memcached
BuildRequires:  python-devel
BuildRequires:	python-django
BuildRequires:	python-mysql
BuildRequires:	translate-toolkit
BuildRequires:	python-distribute
BuildRequires:	python-Sphinx
BuildRequires:	python-cssmin
BuildRequires:	python-django-assets
BuildRequires:	webassets
BuildRequires:	python-django-voting
BuildRequires:	iso-codes
Requires:	apache2-prefork
Requires:	apache2-mod_wsgi
Requires:	iso-codes
Requires:	mysql
Requires:	python-cssmin
Requires:	python-django-assets
Requires:	webassets
Requires:	python-django-voting
Requires:	python-django-south
Requires:	python-lxml
Requires:	python-mysql
Requires:	python-ldap
Requires:	translate-toolkit
Requires:	unzip, zip
Requires:   python-django-jollaaddons
Suggests:	bzr, cvs, darcs, gaupol, git-core, mercurial, subversion
%{py_requires}

%description
Pootle is used to create program translations.
It uses the Translate Toolkit to get access to translation files and therefore
can edit a variety of files (including PO and XLIFF files).

Authors/Credits:
----------------
    See /usr/share/doc/packages/pootle/CREDITS


%package -n pootle-tutorial
Group: Development/Tools/Other
Summary: Pootle tutorial project
Requires:	pootle
%description -n pootle-tutorial
Tutorial project where users can play with Pootle and learn more about
translation and localisation.

%package -n pootle-terminology
Group: Development/Tools/Other
Summary: Pootle terminology files
Requires:	pootle
%description -n pootle-terminology
Gnome terminology files included with pootle sources. For translation memory.

%prep
%setup -q -n %{us_name}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
# workaround to make webassets look for assets in correct directory
echo "STATIC_ROOT = 'pootle/static'" > pootle/settings/91-build-local.conf
%{__python} manage.py assets build
%{__rm} pootle/settings/91-build-local.conf

%{__python} setup.py build_mo
%{__python} setup.py build
%{__python} setup.py build_sphinx

%install
%{__python} setup.py install --skip-build --prefix=%{_prefix} --root=%{buildroot}
%{__install} -D -m0644 %{S:2} %{buildroot}%{ap_sysconfdir}/conf.d/%(basename %{S:2})
%{__install} -D -m0644 %{S:3} %{buildroot}%{ap_sysconfdir}/vhosts.d/%{name}.conf
%{__install} -D -m0644 %{S:6} %{buildroot}%{ap_sysconfdir}/vhosts.d/%{name}-ssl.conf
%{__cp} -p %{S:4} .
%{__install} -d %{buildroot}%{varlib}/%{name}
%{__mv} %{buildroot}%{python_sitelib}/%{name}/po %{buildroot}%{varlib}/%{name}/
%{__install} -D %{S:5} %{buildroot}%{_datadir}/%{name}/%(basename %{S:5})
%{__install} -d %{buildroot}%{_datadir}/%{name}/assets
%{__install} -D %{S:1} %{buildroot}%{_sysconfdir}/%{name}/%(basename %{S:1})
ln -s %{_sysconfdir}/%{name}/localsettings.conf %{buildroot}%{python_sitelib}/%{name}/settings/90-local.conf
%{__mv} %{buildroot}%{python_sitelib}/%{name}/static %{buildroot}%{_datadir}/%{name}

%post
# insert paths in config files
%{__sed} -i -e "s,@name@,%{name},g" -e "s,@datadir@,%{_datadir},g" \
  -e "s,@varlib@,%{varlib},g" -e "s,@libexecdir@,%{ap_libexecdir},g" \
  %{ap_sysconfdir}/conf.d/%(basename %{S:2})
%{__sed} -i -e "s,@name@,%{name},g" -e "s,@datadir@,%{_datadir},g" \
  -e "s,@varlib@,%{varlib},g" -e "s,@hostname@,$(%{__cat} /etc/HOSTNAME),g" \
  %{ap_sysconfdir}/vhosts.d/pootle.conf
%{__sed} -i -e "s,@name@,%{name},g" -e "s,@datadir@,%{_datadir},g" \
  -e "s,@varlib@,%{varlib},g" -e "s,@hostname@,$(%{__cat} /etc/HOSTNAME),g" \
  %{ap_sysconfdir}/vhosts.d/pootle-ssl.conf
%{__sed} -i -e "s,@name@,%{name},g" -e "s,@datadir@,%{_datadir},g" -e "s,@varlib@,%{varlib},g" \
  -e "s,@hostname@,$(%{__cat} /etc/HOSTNAME),g" %{_sysconfdir}/%{name}/localsettings.conf

# Apache needs write permission to /var/lib/pootle/po
%{__mkdir} -p %{varlib}/%{name}/po
%{__chown} %{ap_usr}:%{ap_grp} %{varlib}/%{name}/po -R


# services
# %{_sbindir}/a2enmod wsgi
/sbin/service httpd restart >/dev/null 2>&1 || :
#/sbin/service memcached restart >/dev/null 2>&1 || :

echo "Read %{_datadir}/doc/packages/%{name}/%(basename %{S:4}) for initial setup"


%post -n pootle-tutorial
%{__chown} %{ap_usr}:%{ap_grp} %{varlib}/%{name}/po/tutorial -R

%post -n pootle-terminology
%{__chown} %{ap_usr}:%{ap_grp} %{varlib}/%{name}/po/terminology -R

%postun
#%restart_on_update memcached
%restart_on_update apache2
echo "warning: Following files or directories have not been removed:
/var/lib/pootle/po
/var/log/apache2/pootle-access.log
/var/log/apache2/pootle-error.log"

%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc docs/changelog.rst LICENSE CREDITS README.rst README.suse build/sphinx/html
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/localsettings.conf
%config(noreplace) %{ap_sysconfdir}/conf.d/%(basename %{S:2})
%config %{ap_sysconfdir}/vhosts.d/%{name}.conf
%config %{ap_sysconfdir}/vhosts.d/%{name}-ssl.conf
%{_bindir}/*
%{python_sitelib}/*
%dir %{_datadir}/%{name}
%dir %{varlib}/%{name}
%dir %{varlib}/%{name}/po
%{_datadir}/%{name}/wsgi.py
%{_datadir}/%{name}/static

%files -n pootle-tutorial
%defattr(-,root,root,-)
%{varlib}/%{name}/po/tutorial

%files -n pootle-terminology
%defattr(-,root,root,-)
%{varlib}/%{name}/po/terminology

%changelog
