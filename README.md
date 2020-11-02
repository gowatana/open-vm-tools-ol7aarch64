# open-vm-tools RPM for Oracle Linux 7 ARM (aarch64)

備忘
* .spec ファイルは、[open-vm-tools-11.0.5-3.0.1.el7.src.rpm](https://yum.oracle.com/repo/OracleLinux/OL7/latest/x86_64/getPackageSource/open-vm-tools-11.0.5-3.0.1.el7.src.rpm) のものを編集した。
* systemd-detect-virt で「vmware」が検知できず「none」になるので、Systemd Unit ファイルの ConditionVirtualization はコメントアウト。


インストール

```
# cat /etc/oracle-release
Oracle Linux Server release 7.9
# uname -r
5.4.17-2011.0.7.el7uek.aarch64
# curl -o /etc/yum.repos.d/open-vm-tools-ol7.repo https://gowatana.github.io/open-vm-tools-ol7aarch64/open-vm-tools-ol7.repo
# yum install -y open-vm-tools
# systemctl start vmtoolsd
```

以上。
