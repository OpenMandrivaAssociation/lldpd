%define with_snmp 0
%define user _lldpd
%define chroot /var/run/lldpd

Summary: implementation of IEEE 802.1ab (LLDP)
Name: lldpd
Version: 0.5.2
Release: %mkrel 1
License: MIT
Group: System/Servers
URL: https://trac.luffy.cx/lldpd/
Source0: http://www.luffy.cx/lldpd/%{name}-%{version}.tar.gz
Source1: lldpd.init
Source2: lldpd.sysconfig
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%if %with_snmp
BuildRequires: net-snmp-devel
Requires:      net-snmp
%endif

BuildRequires: libxml2-devel
Requires:      libxml2

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
%{__aclocal} -I m4 --install
%{__autoconf} --force
%{__automake} --force
%configure \
   --with-xml \
%if %with_snmp
   --with-snmp \
%endif
   --enable-cdp \
   --enable-edp \
   --enable-sonmp \
   --enable-fdp \
   --enable-lldpmed \
   --enable-dot1 \
   --enable-dot3 \
   --with-privsep-user=%{user} \
   --with-privsep-group=%{user} \
   --with-privsep-chroot=%{chroot} \
   --prefix=/usr --localstatedir=%{chroot} --sysconfdir=/etc --libdir=%{_libdir}

[ -f /usr/include/net-snmp/agent/struct.h ] || touch src/struct.h
%make

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}
install -d -m770  %{buildroot}/%{chroot}
install -d %{buildroot}/etc/rc.d/init.d
install -d %{buildroot}/etc/sysconfig
install -m644 %{SOURCE2} %{buildroot}/etc/sysconfig/lldpd
install -m755 %{SOURCE1} %{buildroot}/etc/rc.d/init.d/lldpd

%pre
%_pre_useradd %{user} %{chroot} /bin/false

%postun
%_postun_userdel %{user}
%_postun_groupdel %{user}

%preun
%_preun_service %{name}

%post
%_post_service %{name}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc CHANGELOG
%doc %_docdir/lldpd/README
%_sbindir/lldpd
%_sbindir/lldpctl
%doc %_mandir/man8/lldp*
%dir %attr(750,root,root) %{chroot}
%config(noreplace) /etc/sysconfig/lldpd
%attr(755,root,root) /etc/rc.d/init.d/*
