# open-vm-tools RPM for Oracle Linux 7 ARM (aarch64)

備忘
* .spec ファイルは、[open-vm-tools-11.0.5-3.0.1.el7.src.rpm](https://yum.oracle.com/repo/OracleLinux/OL7/latest/x86_64/getPackageSource/open-vm-tools-11.0.5-3.0.1.el7.src.rpm) のものを編集した。
* 11.0.5 は ARM 未対応だったので、最新版 11.1.5 を利用。
* systemd-detect-virt で「vmware」が検知できず「none」になるので、Systemd Unit ファイルの ConditionVirtualization はコメントアウト。


インストール

```
# cat /etc/oracle-release
Oracle Linux Server release 7.9
# uname -r
5.4.17-2011.0.7.el7uek.aarch64
# yum install -y https://github.com/gowatana/open-vm-tools-ol7aarch64/raw/main/RPMS/aarch64/open-vm-tools-11.1.5-1.gowatana.el7.aarch64.rpm
# systemctl start vmtoolsd
```

以上。
