################################################################################
### Copyright 2013-18 VMware, Inc.  All rights reserved.
###
### RPM SPEC file for building open-vm-tools packages.
###
###
### This program is free software; you can redistribute it and/or modify
### it under the terms of version 2 of the GNU General Public License as
### published by the Free Software Foundation.
###
### This program is distributed in the hope that it will be useful,
### but WITHOUT ANY WARRANTY; without even the implied warranty of
### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
### GNU General Public License for more details.
###
### You should have received a copy of the GNU General Public License
### along with this program; if not, write to the Free Software
### Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
################################################################################

%global _hardened_build 1
%global majorversion    11.2
%global minorversion    0
%global toolsbuild      16938113
%global toolsversion    %{majorversion}.%{minorversion}
%global toolsdaemon     vmtoolsd
%global vgauthdaemon    vgauthd

Name:             open-vm-tools
Version:          %{toolsversion}
Release:          1.gowatana%{?dist}
Summary:          Open Virtual Machine Tools for virtual machines hosted on VMware
Group:            Applications/System
License:          GPLv2
URL:              https://github.com/vmware/%{name}
Source0:          https://github.com/vmware/%{name}/releases/download/stable-%{version}/%{name}-%{version}-%{toolsbuild}.tar.gz
Source1:          %{toolsdaemon}.service
Source2:          %{vgauthdaemon}.service
Source3:          run-vmblock\x2dfuse.mount
Source4:          open-vm-tools.conf

ExclusiveArch:    aarch64

Patch107: add-vmware-udev-rule-for-scsi-devices.patch
Patch108: fix-vmware-udev-rule-for-scsi-devices.patch
Patch109: 0001-fix-spaces-in-vmware-udev-rule-for-scsi-devices.patch

BuildRequires:    autoconf
BuildRequires:    automake
BuildRequires:    libtool
BuildRequires:    gcc-c++
BuildRequires:    doxygen
# Fuse is optional and enables vmblock-fuse
BuildRequires:    fuse-devel
BuildRequires:    glib2-devel >= 2.14.0
BuildRequires:    gtk3-devel >= 3.10.0
BuildRequires:    gtkmm30-devel >= 3.10.0
BuildRequires:    libdnet-devel
BuildRequires:    libicu-devel
BuildRequires:    libmspack-devel
# Unfortunately, xmlsec1-openssl does not add libtool-ltdl
# dependency, so we need to add it ourselves.
BuildRequires:    libtool-ltdl-devel
BuildRequires:    libX11-devel
BuildRequires:    libXext-devel
BuildRequires:    libXi-devel
BuildRequires:    libXinerama-devel
BuildRequires:    libXrandr-devel
BuildRequires:    libXrender-devel
BuildRequires:    libXtst-devel
BuildRequires:    openssl-devel
BuildRequires:    pam-devel
BuildRequires:    procps-devel
BuildRequires:    systemd
BuildRequires:    xmlsec1-openssl-devel

Requires:         coreutils
Requires:         fuse
Requires:         libdrm
Requires:         iproute
Requires:         grep
Requires:         pciutils
Requires:         sed
Requires:         systemd
Requires:         systemd-libs
Requires:         tar
Requires:         which
# xmlsec1-openssl needs to be added explicitly
Requires:         xmlsec1-openssl

# For proper install/uninstall
Requires(post):   /sbin/ldconfig
Requires(postun): /sbin/ldconfig 
# open-vm-tools >= 10.0.0 do not require open-vm-tools-deploypkg
# provided by VMware. That functionality is now available as part
# of open-vm-tools package itself.
Obsoletes:        open-vm-tools-deploypkg <= 10.0.5

%description
The %{name} project is an open source implementation of VMware Tools. It
is a suite of open source virtualization utilities and drivers to improve the
functionality, user experience and administration of VMware virtual machines.
This package contains only the core user-space programs and libraries of
%{name}.

%package          desktop
Summary:          User experience components for Open Virtual Machine Tools
Group:            System Environment/Libraries
Requires:         %{name}%{?_isa} = %{version}-%{release}

%description      desktop
This package contains only the user-space programs and libraries of
%{name} that are essential for improved user experience of VMware virtual
machines.

%package          devel
Summary:          Development libraries for Open Virtual Machine Tools
Group:            Development/Libraries
Requires:         %{name}%{?_isa} = %{version}-%{release}

%description      devel
This package contains only the user-space programs and libraries of
%{name} that are essential for developing customized applications for
VMware virtual machines.

%package          test
Summary:          Test utilities for Open Virtual Machine Tools
Group:            Development/Libraries
Requires:         %{name}%{?_isa} = %{version}-%{release}

%description      test
This package contains only the test utilities for %{name} that are
useful for verifying the functioning of %{name} in VMware virtual
machines.

%prep
%autosetup -p2 -n %{name}-%{version}-%{toolsbuild}

%build
# Required for regenerating configure script when
# configure.ac get modified
autoreconf -vif

%global usetirpc without-tirpc

%configure \
    --without-kernel-modules \
    --enable-xmlsec1 \
    --enable-resolutionkms \
    --without-tirpc \
    --disable-static

sed -i -e 's! -shared ! -Wl,--as-needed\0!g' libtool
%make_build

%install
export DONT_STRIP=1
%make_install

# Remove exec bit from config files
chmod a-x %{buildroot}%{_sysconfdir}/pam.d/*
chmod a-x %{buildroot}%{_sysconfdir}/vmware-tools/*.conf
chmod a-x %{buildroot}%{_sysconfdir}/vmware-tools/vgauth/schemas/*

# Remove exec bit on udev rules.
chmod a-x %{buildroot}%{_udevrulesdir}/99-vmware-scsi-udev.rules

# Remove the DOS line endings
sed -i "s|\r||g" README

# Remove "Encoding" key from the "Desktop Entry"
sed -i "s|^Encoding.*$||g" %{buildroot}%{_sysconfdir}/xdg/autostart/vmware-user.desktop

# Remove unnecessary files from packaging
find %{buildroot}%{_libdir} -name '*.la' -delete
rm -fr %{buildroot}%{_defaultdocdir}
rm -f docs/api/build/html/FreeSans.ttf

# Remove mount.vmhgfs & symlink
rm -fr %{buildroot}%{_sbindir} %{buildroot}/sbin/mount.vmhgfs

# Move vm-support to /usr/bin
#mv %{buildroot}%{_sysconfdir}/vmware-tools/vm-support %{buildroot}%{_bindir}

# Systemd unit files
install -p -m 644 -D %{SOURCE1} %{buildroot}%{_unitdir}/%{toolsdaemon}.service
install -p -m 644 -D %{SOURCE2} %{buildroot}%{_unitdir}/%{vgauthdaemon}.service
install -p -m 644 -D '%{SOURCE3}' %{buildroot}%{_unitdir}/run-vmblock\\x2dfuse.mount
install -p -m 644 -D %{SOURCE4} %{buildroot}/usr/lib/modules-load.d/open-vm-tools.conf
# Vmware udev rule for scsi devices
mkdir -p %{buildroot}%{_sysconfdir}/udev/rules.d/
install -p -m 644 -D 99-vmware-scsi-timeout.rules %{buildroot}%{_sysconfdir}/udev/rules.d/99-vmware-scsi-timeout.rules


# 'make check' in open-vm-tools rebuilds docs and ends up regenerating
# the font file. We can add %%check secion once 'make check' is fixed
# upstream

%post
/sbin/ldconfig
# Setup mount point for Shared Folders
# NOTE: Use systemd-detect-virt to detect VMware platform because
#       vmware-checkvm might misbehave on non-VMware platforms.
if [ -f %{_bindir}/vmware-checkvm -a                     \
     -f %{_bindir}/vmhgfs-fuse ] &&                      \
   %{_bindir}/systemd-detect-virt | grep -iq VMware &&   \
   %{_bindir}/vmware-checkvm &> /dev/null &&             \
   %{_bindir}/vmware-checkvm -p | grep -q Workstation && \
   %{_bindir}/vmhgfs-fuse -e &> /dev/null; then
   mkdir -p /mnt/hgfs
fi

if [ "$1" = "2" ]; then
   # Cleanup GuestProxy certs, relevant for upgrades only
   if [ -f %{_bindir}/vmware-guestproxycerttool ]; then
      %{_bindir}/vmware-guestproxycerttool -e &> /dev/null || /bin/true
   fi
   if [ -d /etc/vmware-tools/GuestProxyData ]; then
      rm -rf /etc/vmware-tools/GuestProxyData &> /dev/null || /bin/true
   fi

   # Cleanup vmtoolsd-init.service in case of upgrades
   %{_bindir}/systemctl disable %{toolsdaemon}-init.service &> /dev/null || /bin/true
fi
%systemd_post %{vgauthdaemon}.service
%systemd_post %{toolsdaemon}.service

%post desktop
%systemd_post run-vmblock\x2dfuse.mount

%preun
%systemd_preun %{toolsdaemon}.service
%systemd_preun %{vgauthdaemon}.service

if [ "$1" = "0" -a                                       \
     -f %{_bindir}/vmware-checkvm ] &&                   \
   %{_bindir}/systemd-detect-virt | grep -iq VMware &&   \
   %{_bindir}/vmware-checkvm &> /dev/null; then

   # Tell VMware that open-vm-tools is being uninstalled
   if [ -f %{_bindir}/vmware-rpctool ]; then
      %{_bindir}/vmware-rpctool 'tools.set.version 0' &> /dev/null || /bin/true
   fi

   # Teardown mount point for Shared Folders
   if [ -d /mnt/hgfs ] &&                               \
      %{_bindir}/vmware-checkvm -p | grep -q Workstation; then
      umount /mnt/hgfs &> /dev/null || /bin/true
      rmdir /mnt/hgfs &> /dev/null || /bin/true
   fi
fi

%preun desktop
%systemd_preun run-vmblock\x2dfuse.mount

%postun
/sbin/ldconfig
%systemd_postun_with_restart %{toolsdaemon}.service
%systemd_postun_with_restart %{vgauthdaemon}.service

%postun desktop
%systemd_postun run-vmblock\x2dfuse.mount

%files
%license COPYING
%doc AUTHORS ChangeLog NEWS README
%config(noreplace) %{_sysconfdir}/pam.d/*
%dir %{_sysconfdir}/vmware-tools/
%dir %{_sysconfdir}/vmware-tools/vgauth
%dir %{_sysconfdir}/vmware-tools/vgauth/schemas
%config(noreplace) %{_sysconfdir}/vmware-tools/*.conf
# Don't expect users to modify example tools.conf file
%config %{_sysconfdir}/vmware-tools/tools.conf.example
# Don't expect users to modify VGAuth schema files
%config %{_sysconfdir}/vmware-tools/vgauth/schemas/*
%{_sysconfdir}/vmware-tools/*-vm-default
%{_sysconfdir}/vmware-tools/scripts
%{_sysconfdir}/vmware-tools/statechange.subr
%{_bindir}/VGAuthService
%{_bindir}/vm-support
%{_bindir}/vmhgfs-fuse
%{_bindir}/vmtoolsd
%{_bindir}/vmware-checkvm
%{_bindir}/vmware-hgfsclient
%{_bindir}/vmware-namespace-cmd
%{_bindir}/vmware-rpctool
%{_bindir}/vmware-toolbox-cmd
%{_bindir}/vmware-vgauth-cmd
%{_bindir}/vmware-xferlogs
%{_libdir}/libDeployPkg.so.*
%{_libdir}/libguestlib.so.*
%{_libdir}/libhgfs.so.*
%{_libdir}/libvgauth.so.*
%{_libdir}/libvmtools.so.*
%dir %{_libdir}/%{name}/
%dir %{_libdir}/%{name}/plugins
%dir %{_libdir}/%{name}/plugins/common
%{_libdir}/%{name}/plugins/common/*.so
%dir %{_libdir}/%{name}/plugins/vmsvc
%{_libdir}/%{name}/plugins/vmsvc/*.so
%{_datadir}/%{name}/
%{_udevrulesdir}/99-vmware-scsi-udev.rules
%{_unitdir}/%{toolsdaemon}.service
%{_sysconfdir}/udev/rules.d/99-vmware-scsi-timeout.rules
%{_unitdir}/%{vgauthdaemon}.service
%{_unitdir}/run-vmblock\x2dfuse.mount
/usr/lib/modules-load.d/open-vm-tools.conf

%files desktop
%{_sysconfdir}/xdg/autostart/*.desktop
%{_bindir}/vmware-user
%{_bindir}/vmware-user-suid-wrapper
%{_bindir}/vmware-vmblock-fuse
%{_libdir}/%{name}/plugins/vmusr/

%files devel
%doc docs/api/build/*
%exclude %{_includedir}/libDeployPkg/
%{_includedir}/vmGuestLib/
%{_libdir}/pkgconfig/*.pc
%{_libdir}/libDeployPkg.so
%{_libdir}/libguestlib.so
%{_libdir}/libhgfs.so
%{_libdir}/libvgauth.so
%{_libdir}/libvmtools.so

%files test
%{_bindir}/vmware-vgauth-smoketest

%changelog
* Mon Nov 02 2020 Go Watanabe <gowatana@vmtn.jp> - 11.2.0-1.gowatana.el7
- update open-vm-tools.

* Wed Oct 14 2020 Go Watanabe <gowatana@vmtn.jp> - 11.1.5-1.gowatana.el7
- Custom Build for ESXi on ARM. - Raspberry Pi 4 B
  This is an experimental build.
  original .spec and files:
  https://yum.oracle.com/repo/OracleLinux/OL7/latest/x86_64/getPackageSource/open-vm-tools-11.0.5-3.0.1.el7.src.rpm

* Tue May 26 2020 David Sloboda <david.x.sloboda@oracle.com> - 11.0.5-3.0.1
- fix spaces in vmware udev rule for scsi devices
  [Orabug: 24461968]
- Fix vmware udev rule in 99-vmware-scsi-timeout.rules file.
  [Orabug: 22815019]
- Increase timeout for scsi devices on VMWare guests by adding a udev rule.
- Created a new file 99-vmware-scsi-timeout.rules
- Modified spec file to install this new file.
  [Orabug: 21819156]

* Tue Apr 07 2020 Miroslav Rezanina <mrezanin@redhat.com> - 11.0.5-3.el7
- ovt-Fix-a-trivial-memory-leak-in-namespacetool.c.patch [bz#1818109]
- ovt-Update-copyright-to-reflect-previous-change.patch [bz#1818109]
- Resolves: bz#1818109
  ([ESXi][RHEL7.9]open-vm-tools coverity scan issue)

* Thu Apr 02 2020 Miroslav Rezanina <mrezanin@redhat.com> - 11.0.5-2.el7
- ovt-Fix-ldconfig-call.patch [bz#1815549]
- ovt-add-appinfo-plugin.patch [bz#1809753]
- Resolves: bz#1809753
  ([ESXi][RHEL7.9]open-vm-tools add appinfo plugin patch)
- Resolves: bz#1815549
  ([ESXi][RHEL7.9]open-vm-tools reports line 1: ?ldconfig: command not found during system installation)

* Tue Mar 17 2020 Miroslav Rezanina <mrezanin@redhat.com> - 11.0.5-1
- Rebase to 11.0.5 [bz#1806675]
- Resolves: bz#1806675
 ([ESXi][RHEL7.9]Rebase open-vm-tools to 11.0.5 for RHEL 7.9)

* Mon Nov 04 2019 Miroslav Rezanina <mrezanin@redhat.com> - 10.3.10-2
- ovt-Fix-memory-leaks-in-vix-tools-plugin.patch [bz#1760625]
- ovt-End-VGAuth-impersonation-in-the-case-of-error.patch [bz#1760625]
- ovt-Fix-leaks-in-ListAliases-and-ListMappedAliases-9bc72.patch [bz#1760625]
- Resolves: bz#1760625
  ([ESXi][RHEL7.8]Need to backport some severe memory leak fixes from upstream)

* Thu Aug 22 2019 Miroslav Rezanina <mrezanin@redhat.com> - 10.3.10-1
- Rebase to 10.3.10 [bz#1725187]
- Resolves: bz#1725187
  ([ESXi][RHEL7.8 ]Rebase open-vm-tools to 10.3.10)

* Wed Mar 13 2019 Miroslav Rezanina <mrezanin@redhat.com> - 10.3.0-2
- ovt-Enable-cloud-init-by-default-to-change-the-systemd-u.patch [bz#1662278]
- ovt-Fix-RELRO-flag.patch [bz#1678576]
- Resolves: bz#1662278
  ([ESXi][RHEL7.7]Enable cloud-init by default to change the systemd unit file vmtoolsd.service)
- Resolves: bz#1678576
  ([ESXi][RHEL7.6] Several files lost Full RELRO)

* Tue Feb 12 2019 Miroslav Rezanina <mrezanin@redhat.com> - 10.3.0-1
- Updated RHEL version
- Resolves: bz#1667549
  ([RHEL 7.7, ESXi] Rebase open-vm-tools to 10.3.0)

* Tue Aug 21 2018 Miroslav Rezanina <mrezanin@redhat.com> - 10-2.5-3
- ovt-Workaround-for-false-negative-result-when-detecting.patch [bz#1601559]
- Resolves: bz#1601559
  ([ESXi][RHEL7.6] Include new open-vm-tools patches for cloud-init to work with python-2)

* Wed May 09 2018 Ravindra Kumar <ravindrakumar@vmware.com> - 10.2.5-2
- Use tirpc for Fedora 28 onwards.

* Wed May 09 2018 Ravindra Kumar <ravindrakumar@vmware.com> - 10.2.5-1
- Package new upstream version open-vm-tools-10.2.5-8068406 (RHBZ#1431376).
- Added use-tirpc.patch to use libtirpc instead of deprecated Sun RPC.
- Removed wayland-crash.patch which is no longer needed.

* Mon Apr 30 2018 Pete Walter <pwalter@fedoraproject.org> - 10.2.0-5
- Rebuild for ICU 61.1

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 10.2.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Fri Dec 29 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.2.0-3
- Patch for a Wayland related crash in the desktopEvents plugin (RHBZ#1526952).
- gdk_set_allowed_backends() is available in version 3.10 and later only.

* Mon Dec 18 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.2.0-2
- Build with gtk3 only on newer distros.

* Fri Dec 15 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.2.0-1
- Package new upstream version open-vm-tools-10.2.0-7253323.
- Remove the patches that are no longer needed.
- New version builds with gtk3 by default.
- Package vmware-user symlink in desktop.
- Add a new test package for test utilities.
- Pick a fix to a conditional from Miroslav Vadkerti <mvadkert@redhat.com>.

* Thu Nov 30 2017 Pete Walter <pwalter@fedoraproject.org> - 10.1.10-4
- Rebuild for ICU 60.1

* Thu Sep 28 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.1.10-3
- Replaced 'net-tools' dependency with 'iproute' (RHBZ#1496134).
- Added resolutionKMS-wayland-2.patch with some new fixes.

* Fri Aug 11 2017 Kalev Lember <klember@redhat.com> - 10.1.10-2
- Bump and rebuild for an rpm signing issue

* Thu Aug 10 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.1.10-1
- Package new upstream version open-vm-tools-10.1.10-6082533.
- Remove the patches that are no longer needed.

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 10.1.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 10.1.5-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jul 25 2017 Richard W.M. Jones <rjones@redhat.com> - 10.1.5-5
- Fix /tmp race conditions in libDeployPkg (CVE-2015-5191).

* Sun Apr 02 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.1.5-4
- ResolutionKMS patch for Wayland (RHBZ#1292234).

* Thu Mar 16 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.1.5-3
- Need to add xmlsec1-openssl dependency explicitly.

* Tue Feb 28 2017 Richard W.M. Jones <rjones@redhat.com> - 10.1.5-2
- Use 0644 permissions for udev rules file.

* Fri Feb 24 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.1.5-1
- Package new upstream version open-vm-tools-10.1.5-5055683 (RHBZ#1408959).

* Fri Feb 17 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.1.0-1
- Package new upstream version open-vm-tools-10.1.0-4449150 (RHBZ#1408959).
- Remove patches that are no longer needed.
- Build with --enable-xmlsec1 to avoid dependency on xerces-c and xml-security-c.
- Replace _prefix/lib/udev/rules.d/ with _udevrulesdir macro.

* Thu Feb 16 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.5-10
- sysmacros patch for glibc-2.25 (RHBZ#1411807).
- vgauth patch for openssl-1.1.0.

* Thu Feb 16 2017 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.5-9
- udev rules patch for longer SCSI timeouts (RHBZ#1214347).

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 10.0.5-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Oct 26 2016 Richard W.M. Jones <rjones@redhat.com> - 10.0.5-5
- vm-support script needs lspci from pciutils (RHBZ#1388766).

* Wed Sep 14 2016 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.5-4
- Patch for HGFS stale caching issues (RHBZ#1342181).

* Mon Jun 20 2016 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.5-3
- Use systemd-detect-virt to detect VMware platform (RHBZ#1251656).

* Wed May 25 2016 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.5-2
- Obsolete open-vm-tools-deploypkg because its not needed for v10.x.

* Wed May 25 2016 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.5-1
- Package new upstream version open-vm-tools-10.0.5-3227872.
- Add a patch for fixing GCC 6 build issue (RHBZ#1305108).
- Replace kill-werror.patch with no-unused-const.patch.

* Wed May 25 2016 Richard W.M. Jones <rjones@redhat.com> - 10.0.0-12
- Bump and rebuild.

* Sat Apr 23 2016 Richard W.M. Jones <rjones@redhat.com> - 10.0.0-11
- Kill -Werror with fire (RHBZ#1305108).

* Fri Apr 15 2016 David Tardon <dtardon@redhat.com> - 10.0.0-10
- rebuild for ICU 57.1

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 10.0.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Oct 28 2015 David Tardon <dtardon@redhat.com> - 10.0.0-8
- rebuild for ICU 56.1

* Thu Oct 01 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.0-7
- Added a missing output redirection

* Thu Oct 01 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.0-6
- Setup Shared Folders mount point when 'vmhgf-fuse -e' is success

* Thu Oct 01 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.0-5
- Setup and teardown Shared Folders mount point on VMs running
  on VMware Workstation or VMware Fusion.

* Wed Sep 30 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.0-4
- vmhgfs-fuse needs 'fusermount' from 'fuse'

* Wed Sep 30 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.0-3
- Replace -std=c++11 with -std=gnu++11 to get "linux" definitions work
  in order to fix the build issue,
  https://kojipkgs.fedoraproject.org//work/tasks/4823/11274823/build.log
- Removed unused definitions for CFLAGS and CXXFLAGS
 
* Wed Sep 30 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.0-2
- Add -std=c++11 to CXXFLAGS for fixing the build issue,
  https://kojipkgs.fedoraproject.org//work/tasks/3685/11273685/build.log

* Tue Sep 29 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 10.0.0-1
- Package new upstream version open-vm-tools-10.0.0-3000743

* Wed Aug 26 2015 Simone Caronni <negativo17@gmail.com> - 9.10.2-2
- Add license macro.
- Remove initscripts requirement (#1226369).
- Delete mount.vmhgfs instead of excluding from packaging, so the debug
  information is not included in the package (#1190540).
- Be more explicit with configuration files, newer mock complains of files being
  listed twice.

* Tue Jul 07 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 9.10.2-1
- Package new upstream version open-vm-tools-9.10.2-2822639
- Removed the patches that are no longer needed

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 9.10.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed May 20 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 9.10.0-4
- Claim ownership for /etc/vmware-tools directory

* Fri May 15 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 9.10.0-3
- Put Fedora 23 specific fix under a conditional, so that the change
  can be backported to other branches easily if required.

* Fri May 08 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 9.10.0-2
- F23 has split gdk-pixbuf2-devel >= 2.31.3-5 into 3 packages, gdk-pixbuf2-devel,
  gdk-pixbuf2-modules-devel, and gdk-pixbuf2-xlib-devel. gtk2-devel does not depend
  on gdk-pixbuf2-xlib-devel. Therefore, we need to pull in gdk-pixbuf2-xlib-devel
  dependency ourselves.

* Thu Apr 30 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 9.10.0-1
- Package new upstream version open-vm-tools-9.10.0-2476743
- New version requires adding a new service vgauthd
- Removed old patches that are no longer needed
- Fix (asm_x86.patch) for correct GCC version check
- Fix (strerror_r.patch) for picking GNU signature of strerror_r
- Fix (toolboxcmd.patch) for compiling toolboxcmd-shrink.c with gcc 5.0.1

* Wed Feb 04 2015 Ravindra Kumar <ravindrakumar@vmware.com> - 9.4.6-6
- Added a patch for missing NetIpRouteConfigInfo (BZ#1189295)

* Mon Jan 26 2015 David Tardon <dtardon@redhat.com> - 9.4.6-5
- rebuild for ICU 54.1

* Wed Sep 24 2014 Simone Caronni <negativo17@gmail.com> - 9.4.6-4
- Rebuild for new procps-ng version.

* Tue Aug 26 2014 David Tardon <dtardon@redhat.com> - 9.4.6-3
- rebuild for ICU 53.1

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 9.4.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Jul 16 2014 Ravindra Kumar <ravindrakumar@vmware.com> - 9.4.6-1 
- Package new upstream version open-vm-tools-9.4.6-1770165
- Added "autoreconf -i" and its build dependencies (autoconf, automake and libtool)
  to generate configure script, this is required for version 9.4.6 as it does not
  have configure script bundled in the tar
- Fix (sizeof_argument.patch) for bad sizeof argument error 

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 9.4.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Apr 23 2014 Ravindra Kumar <ravindrakumar@vmware.com> - 9.4.0-9
- Removed unnecessary package dependency on 'dbus'
- Moved 'vm-support' script to /usr/bin
- Added a call to 'tools.set.version' RPC to inform VMware
  platform when open-vm-tools has been uninstalled

* Wed Mar 26 2014 Ravindra Kumar <ravindrakumar@vmware.com> - 9.4.0-8
- Add missing package dependency on 'which' (BZ#1045709)

* Tue Mar 25 2014 Ravindra Kumar <ravindrakumar@vmware.com> - 9.4.0-7
- Add -D_DEFAULT_SOURCE to suppress warning as suggested in
  https://sourceware.org/bugzilla/show_bug.cgi?id=16632

* Fri Mar 21 2014 Ravindra Kumar <ravindrakumar@vmware.com> - 9.4.0-6
- Add missing package dependencies (BZ#1045709, BZ#1077320)

* Tue Feb 18 2014 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 9.4.0-5
- Fix FTBFS g_info redefine (RHBZ #1063847)

* Fri Feb 14 2014 David Tardon <dtardon@redhat.com> - 9.4.0-4
- rebuild for new ICU

* Tue Feb 11 2014 Richard W.M. Jones <rjones@redhat.com> - 9.4.0-3
- Only build on x86-64 for RHEL 7 (RHBZ#1054608).

* Wed Dec 04 2013 Richard W.M. Jones <rjones@redhat.com> - 9.4.0-2
- Rebuild for procps SONAME bump.

* Wed Nov 06 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.4.0-1
- Package new upstream version open-vm-tools-9.4.0-1280544.
- Added CUSTOM_PROCPS_NAME=procps and -Wno-deprecated-declarations
  for version 9.4.0.

* Thu Aug 22 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-11
- Added copyright and license text.
- Corrected summary for all packages. 

* Thu Aug 08 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-10
- Added options for hardening build (bug 990549). 
- Excluded unwanted file mount.vmhgfs from packaging (bug 990547).
- Removed deprecated key "Encoding" from "Desktop Entry" (bug 990552).

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 9.2.3-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jun  4 2013 Richard W.M. Jones <rjones@redhat.com> - 9.2.3-8
- RHEL 7 now includes libdnet, so re-enable it.

* Fri May 24 2013 Richard W.M. Jones <rjones@redhat.com> - 9.2.3-6
- +BR gcc-c++.  If this is missing it fails to build.
- On RHEL, disable libdnet.

* Mon May 06 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-5
- Renamed source file open-vm-tools.service -> vmtoolsd.service
  to match it with the service name.

* Wed May 01 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-4
- Bumped the release to pick the new service definition with
  no restart directive.

* Mon Apr 29 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-3
- open-vm-tools-9.2.3 require glib-2.14.0.

* Mon Apr 29 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-2
- Bumped the release to pick the new service definition.

* Thu Apr 25 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.3-1
- Package new upstream version open-vm-tools-9.2.3-1031360.
- Removed configure options CUSTOM_PROCPS_NAME (for libproc) and
  -Wno-deprecated-declarations as these have been addressed in
  open-vm-tools-9.2.3-1031360.

* Wed Apr 24 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-12
- Removed %%defattr and BuildRoot.
- Added ExclusiveArch.
- Replaced /usr/sbin/ldconfig with /sbin/ldconfig.

* Mon Apr 22 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-11
- Removed the conditional steps for old versions of Fedora and RHEL.

* Thu Apr 18 2013 Ravindra Kumar <ravindrakumar at vmware.com> - 9.2.2-10
- Addressed formal review comments from Simone Caronni.
- Removed %%check section because 'make check' brings font file back.

* Wed Apr 17 2013 Simone Caronni <negativo17@gmail.com> - 9.2.2-9
- Removed rm command in %%check section.
- Remove blank character at the beginning of each changelog line.

* Mon Apr 15 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-8
- Removed FreeSans.ttf font file from packaging.
- Added 'rm' command to remove font file in %%check section because
  'make check' adds it back.
- Added doxygen dependency back.

* Thu Apr 11 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-7
- Applied patch from Simone for removal of --docdir option from configure.
- Removed unnecessary --enable-docs option from configure.
- Removed doxygen dependency.

* Thu Apr 11 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-6
- Replaced vmtoolsd with a variable.
- Changed summary for subpackages to be more specific.
- Removed drivers.txt file as we don't really need it.
- Fixed vmGuestLib ownership for devel package.
- Removed systemd-sysv from Requires for Fedora 18+ and RHEL 7+.
- Made all "if" conditions consistent.

* Wed Apr 10 2013 Simone Caronni <negativo17@gmail.com> - 9.2.2-5
- Added RHEL 5/6 init script.
- Renamed SysV init script / systemd service file to vmtoolsd.
- Fixed ownership of files from review.
- Moved api documentation in devel subpackage.
- Removed static libraries.

* Tue Apr 09 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-4
- Applied part of review fixes patch from Simone Caronni for systemd setup.
- Replaced tabs with spaces all over.

* Tue Apr 09 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-3
- Applied review fixes patch from Simone Caronni.
- Added missing *.a and *.so files for devel package.
- Removed unnecessary *.la plugin files from base package.

* Mon Apr 08 2013 Ravindra Kumar <ravindrakumar@vmware.com> - 9.2.2-2
- Modified SPEC to follow the conventions and guidelines.
- Addressed review comments from Mohamed El Morabity.
- Added systemd script.
- Verified and built the RPMS for Fedora 18.
- Fixed rpmlint warnings.
- Split the UX components in a separate package for desktops.
- Split the help files in a separate package for help.
- Split the guestlib headers in a separate devel package.

* Mon Jan 28 2013 Sankar Tanguturi <stanguturi@vmware.com> - 9.2.2-1
- Initial SPEC file to build open-vm-tools for Fedora 17.
