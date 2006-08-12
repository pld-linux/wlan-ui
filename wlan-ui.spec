#
# TODO:
# - .desktop
#
%include	/usr/lib/rpm/macros.perl
Summary:	wlan-ui - UI for selecting and connecting to WLAN access points (APs)
Summary(pl):	wlan-ui - interfejs u¿ytkownika do wybierania i ³±czenia siê z AP WLAN-ów
Name:		wlan-ui
Version:	0.5
Release:	1
License:	Perl Artistic License
Group:		Applications/Networking
Source0:	http://dl.sourceforge.net/wlan-ui/%{name}.pl
# Source0-md5:	73f1082f42b0068d68dcc7af11574019
Patch0:		%{name}-rt2x00.patch
URL:		http://wlan-ui.sourceforge.net/
BuildRequires:	perl-tools-pod
BuildRequires:	rpm-perlprov >= 4.1-13
Requires:	dhcpcd
Requires:	module-init-tools
Requires:	net-tools
Requires:	pci-database
Requires:	procps
Requires:	wireless-tools
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
wlan-ui.pl is a program to connect to wireless networks. It can be run
as a GUI which will offer a list of available networks to connect to.

%description -l pl
wlan-ui.pl to program do ³±czenia siê z sieciami bezprzewodowymi. Mo¿e
byæ uruchamiany jako graficzny interfejs u¿ytkownika oferuj±cy listê
dostêpnych sieci do po³±czenia siê z nimi.

%prep
%setup -q -c -T
cp %{SOURCE0} .
%patch0 -p0

%build
pod2man -s 1 %{SOURCE0} >%{name}.1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_mandir}/man1,%{_sysconfdir}}

install *.pl $RPM_BUILD_ROOT%{_bindir}
install *.1 $RPM_BUILD_ROOT%{_mandir}/man1

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
		exec sudo $command "$@"
	elif (try_gnomesu $command); then
		exec gnomesu $command "$@"
	else
		exec $command "$@"
	fi
else
	exec $command "$@"
fi
EOF

cat <<'EOF' >$RPM_BUILD_ROOT%{_sysconfdir}/%{name}rc
# configuration for %{name}

# Wireless driver module to load
#$MODULE = 'ipw2200';
$MODULE = undef; 

# Module parameters
$MODULEPARAMS = '';

# Wireless network device - e.g. 'wlan0'.
# If not defined we use /proc/net/wireless to find the device
$DEVICE = undef;

# Commands for manipulating wlan module etc
# We will find unspecified commands from the path
$CMDS = {
  'lsmod',    '/sbin/lsmod',
  'modprobe', '/sbin/modprobe',
  'load',     undef,              # modprobe used by default
  'unload',   undef,              # modprobe -r used by default
  'iwconfig', '/sbin/iwconfig',
  'iwlist',   '/sbin/iwlist',
  'ifconfig', '/sbin/ifconfig',
  'ps',       undef,
  'dhcpcd',   '/sbin/dhcpcd',
  'pcidev',   '/usr/bin/pcidev',
};

$MODULE ||= try_to_find_module();    # fallback

sub try_to_find_module {
  if (defined $CMDS->{pcidev} && -x $CMDS->{pcidev}) {
    for (grep /wireless|wlan|802\S*11/i, `$CMDS->{pcidev} net`) {
      chomp;
      next unless /^\S+\s+(\S+)\s+(.+?)\s*$/;
      my ($module, $device) = ($1, $2);
      warn "$0: using module '$1' for device '$2'\n";
      return $1;
    }
  }
  undef;
}

# vim: filetype=perl
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*
%{_mandir}/man1/*
