#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.template.loader import render_to_string
from lib.common import GetRedis
from monitor.utils.wx import wx
import json


@shared_task()
def alert_task(alert_data, users):
    res = GetRedis.connect()
    res_key = str(hash(str(users)))  # to be unique ?
    if res.get("alert_{0}".format(res_key)) == 1:
        return True

    res.set("alert_{0}".format(res_key), 1)  # set status running
    try:
        msg = render_to_string("monitor/wx2.html.j2",
                               {"data": alert_data,
                                "users": ', '.join([str(u) for u in list(users)[:10]])
                                })
        # labels = ["zabbix", "prometheus", "elasticsearch", "xxl-job", "else"]
        # subject = "`{}` `{}    `".format(labels[alert_data.get("source")],
        #                                  str(alert_data.get("ip"))[0:15])
        status_code = alert_data.get("status_code")
        if 0 == status_code:
            subject = "> `{}` `{}    `".format(
                alert_data.get("status"),
                str(alert_data.get("ip"))[0:15]
            )
        else:
            subject = '> <font color="info">{}  {}</font>'.format(alert_data.get("status"),
                                                                  str(alert_data.get("ip"))[0:15])
        to_list = [u.wid for u in users if u.wid]
        for receiver in to_list:
            wx(receiver, subject, msg)
    finally:
        res.set("alert_{0}".format(res_key), 0)
        res.set("alert_data_{0}".format(res_key), json.dumps(alert_data, indent=4))
        res.set("alert_users_{0}".format(res_key),
                ','.join([str(u) for u in users]))

    return True
