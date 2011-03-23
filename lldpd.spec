# configure options
%define lldpd_user _lldpd
%define lldpd_group _lldpd
%define lldpd_chroot /var/run/lldpd

Summary: implementation of IEEE 802.1ab (LLDP)
Name: lldpd
Version: 0.5.2
Release: %mkrel 0
License: MIT
Group: System/Servers
URL: https://trac.luffy.cx/lldpd/
Source0: http://www.luffy.cx/lldpd/%{name}-%{version}.tar.gz
Source1: lldpd.init
Source2: lldpd.sysconfig

BuildRequires: net-snmp-devel
Requires:      net-snmp
BuildRequires: libxml2-devel
Requires:      libxml2

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}

%description
This implementation provides LLDP sending and reception, supports VLAN
and includes an SNMP subagent that can interface to an SNMP agent
through AgentX protocol.

LLDP is an industry standard protocol designed to supplant proprietary
Link-Layer protocols such as Extreme EDP (Extreme Discovery Protocol)
and CDP (Cisco Discovery Protocol). The goal of LLDP is to provide an
inter-vendor compatible mechanism to deliver Link-Layer notifications
to adjacent network devices.

This daemon is also able to deal with CDP, FDP, SONMP and EDP
protocol. It also handles LLDP-MED extension.

%prep
%setup -q
%build
%{__aclocal} -I ./m4 --install
%{__autoconf} --force
%{__automake} --force
%configure \
   --with-xml \
   --with-snmp \
   --enable-cdp \
   --enable-edp \
   --enable-sonmp \
   --enable-fdp \
   --enable-lldpmed \
   --enable-dot1 \
   --enable-dot3 \
   --with-privsep-user=%lldpd_user \
   --with-privsep-group=%lldpd_group \
   --with-privsep-chroot=%lldpd_chroot \
   --prefix=/usr --localstatedir=%lldpd_chroot --sysconfdir=/etc --libdir=%{_libdir}

[ -f /usr/include/net-snmp/agent/struct.h ] || touch src/struct.h
%make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
install -d -m770  $RPM_BUILD_ROOT/%lldpd_chroot
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install -d $RPM_BUILD_ROOT/etc/sysconfig
install -m644 %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/lldpd
install -m755 %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/lldpd

%pre
# Create lldpd user/group
if getent group %lldpd_group >/dev/null 2>&1 ; then : ; else \
 /usr/sbin/groupadd -r %lldpd_group > /dev/null 2>&1 || exit 1 ; fi
if getent passwd %lldpd_user >/dev/null 2>&1 ; then : ; else \
 /usr/sbin/useradd -g %lldpd_group -M -r -s /bin/false \
 -c "LLDP daemon" -d %lldpd_chroot %lldpd_user 2> /dev/null \
 || exit 1 ; fi

%post
/sbin/chkconfig --add lldpd

%postun
if [ "$1" -ge  "1" ]; then
   /etc/rc.d/init.d/lldpd  condrestart >/dev/null 2>&1
fi

%preun
if [ "$1" = "0" ]; then
   /sbin/chkconfig --del lldpd
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc CHANGELOG 
%doc %_docdir/lldpd/README
%_sbindir/lldpd 
%_sbindir/lldpctl
%doc %_mandir/man8/lldp*
%dir %attr(750,root,root) %lldpd_chroot
%config(noreplace) /etc/sysconfig/lldpd
%attr(755,root,root) /etc/rc.d/init.d/*
