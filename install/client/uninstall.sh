#!/bin/bash
set -e
echo "####stop alertd service####"
service alertd stop
work_dir=/var/opt/alerts/client
rm -rf $work_dir
os=$(cat /proc/version)
if (echo $os|grep centos) || (echo $os|grep 'Red Hat')
then
    rm -rf /var/lib/systemd/system/alertd.service
    rm -rf /etc/init.d/alertd
    rm -rf /var/opt/alerts/client
elif (echo $os|grep Ubuntu)
then
    rm -rf /etc/systemd/system/alertd.service
    rm -rf /var/opt/alerts/client
else
    echo "your os version is not supported!"
fi
echo "####admiset agent uninstall finished!####"
