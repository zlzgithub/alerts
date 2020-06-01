#!/bin/bash
/usr/bin/celery multi start w1 w2 -c 2 --app=alerts --logfile="/var/opt/alerts/logs/%n%I.log" --pidfile=/var/opt/alerts/pid/%n.pid

