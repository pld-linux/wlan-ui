#
# TODO:
# - .desktop
# - sudo / gnomesu support
#
%include	/usr/lib/rpm/macros.perl
Summary:	wlan-ui - UI for selecting and connecting to WLAN access points (APs)
#Summary(pl):	
Name:		wlan-ui
Version:	0.5
Release:	1
License:	Perl Artistic License
Group:		Applications/Networking
Source0:	http://dl.sourceforge.net/wlan-ui/%{name}.pl
# Source0-md5:	73f1082f42b0068d68dcc7af11574019
URL:		http://wlan-ui.sourceforge.net/
BuildRequires:	perl-tools-pod
BuildRequires:	rpm-perlprov >= 4.1-13
Requires:	dhcpcd
Requires:	module-init-tools
Requires:	net-tools
Requires:	procps
Requires:	wireless-tools
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
wlan-ui.pl is a program to connect to wireless networks.  It can be run
as a GUI which will offer a list of available networks to connect to.

#%description -l pl

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1}

install      %{SOURCE0}  $RPM_BUILD_ROOT%{_bindir}/
pod2man -s 1 %{SOURCE0} >$RPM_BUILD_ROOT%{_mandir}/man1/%{name}.1

cat <<'EOF' >$RPM_BUILD_ROOT%{_bindir}/%{name}
#!/bin/sh
try_sudo()
{
	cmd="$1"
	helper=`whence -p sudo`
	[ -n "$helper" -a -x "$helper" ] || return 1
	$helper -l | egrep -q \
		'^[[:blank:]]*\([^[:blank:]]+\)[[:blank:]]+NOPASSWD:[[:blank:]]+(ALL|'$cmd')'
	return $?
}

try_gnomesu()
{
	cmd="$1"
	helper=`whence -p gnomesu`
	[ -n "$helper" -a -x "$helper" ] || return 1
	return 0
}

command=%{_bindir}/%{name}.pl

if [ "`id -u`" -gt 0 ]; then
	if (try_sudo $command); then
		exec sudo $command
	elif (try_gnomesu $command); then
		exec gnomesu $command
	else
		exec $command
	fi
else
	exec $command
fi
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%{_mandir}/man1/*
