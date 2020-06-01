#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import urllib

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts.permission import permission_verify
from cmdb.models import Host, HostService, ServiceSystem, SystemGroup
from models import Problem, Notification
from monitor.health_api import get_metric_all_service_data, get_overview_systems_data, \
    get_all_service_data, get_all_host_data, get_plat_name, get_metric_service_index_hosts_data, \
    get_metric_index_hosts_data

MAX_ITEMS = 500


def refresh_time_rng(request, max_days=0):
    global time_rng, cookie_time_rng
    default_days = 1
    if request.method == 'GET' and request.GET.get('fr') == 'wx':
        cookie_time_rng = ""
        default_days = 6
    else:
        cookie_time_rng = request.COOKIES.get('time-rng')

    if cookie_time_rng:
        st, fn = urllib.unquote(cookie_time_rng).split(' -- ')
        d_fn = datetime.datetime.strptime(fn, '%Y-%m-%d')
        fn2 = (d_fn + datetime.timedelta(days=1)).strftime("%F")
        if max_days:
            d_st = datetime.datetime.strptime(st, '%Y-%m-%d')
            d_st2 = d_fn - datetime.timedelta(days=max_days)
            st = (max(d_st, d_st2)).strftime("%F")
        time_rng = [st, fn2]
    else:
        st = (datetime.datetime.now() + datetime.timedelta(days=-default_days)).strftime("%F")
        fn = datetime.datetime.now().strftime("%F")
        d_fn = datetime.datetime.now() + datetime.timedelta(days=1)
        fn2 = d_fn.strftime("%F")
        time_rng = [st, fn2]
        cookie_time_rng = " -- ".join([st, fn])


@login_required()
@permission_verify()
def overview_systems(request):
    refresh_time_rng(request)
    resp = get_overview_systems_data()
    return render(request, "monitor/health-overview.html", resp)


@login_required()
@permission_verify()
def overview_services(request):
    refresh_time_rng(request)
    result = get_all_service_data()
    resp = render(request, "monitor/health-overview-services.html", result)
    return resp


@login_required()
@permission_verify()
def overview_hosts(request):
    refresh_time_rng(request)
    result = get_all_host_data()
    return render(request, "monitor/health-overview-hosts.html", result)


@login_required()
@permission_verify()
def overview_problems(request):
    refresh_time_rng(request)
    cur_time_rng = time_rng
    plat_name = get_plat_name(request)
    url_get_items = "/monitor/health/getproblems/"
    return render(request, "monitor/health-overview-problems.html", locals())


@login_required()
@permission_verify()
def overview_notifications(request):
    refresh_time_rng(request)
    plat_id = request.COOKIES.get('plat') or ""
    plat_id = urllib.unquote(plat_id)
    aria_controls_id = request.COOKIES.get('aria_controls') or ""
    aria_controls_id = urllib.unquote(aria_controls_id)
    if str(aria_controls_id).startswith('multiCollapse-'):
        aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
    else:
        aria_controls_id = ""

    if aria_controls_id:
        plat_name = SystemGroup.objects.get(id=aria_controls_id).name
    elif plat_id:
        plat_name = SystemGroup.objects.get(id=int(plat_id)).name
    else:
        plat_name = u"所有"

    cur_time_rng = time_rng
    url_get_items = "/monitor/health/getnotifications/"
    return render(request, "monitor/health-overview-notifications.html", locals())


@login_required()
@permission_verify()
def index_services(request, system_id):
    refresh_time_rng(request)
    result = get_all_service_data(system_id)
    resp = render(request, "monitor/health-service.html", result)
    resp.set_cookie("system_id", system_id)
    return resp


@login_required()
@permission_verify()
def index_hosts(request, service_id):
    refresh_time_rng(request)
    sys = None
    system_id = request.COOKIES.get('system_id')
    if system_id and "-1" != system_id:
        sys = ServiceSystem.objects.get(id=system_id)
    result = get_all_host_data(service_id)
    if sys:
        result['sys'] = sys
    resp = render(request, "monitor/health-host.html", result)
    resp.set_cookie("service_id", service_id)
    return resp


@login_required()
@permission_verify()
def index_problems(request, host_id):
    refresh_time_rng(request)
    sys = None
    svc = None
    system_id = request.COOKIES.get('system_id')
    service_id = request.COOKIES.get('service_id')
    if system_id and "-1" != system_id:
        sys = ServiceSystem.objects.get(id=system_id)
    if service_id and "-1" != service_id:
        svc = HostService.objects.get(id=service_id)

    host = Host.objects.get(id=host_id)
    allhost = [host]
    host_problems_dict = {}
    host_problems_list = []
    for host in allhost:
        try:
            problems = Problem.objects.filter(ip=host.ip,
                                              create_time__range=time_rng)[:MAX_ITEMS]
            host_problems_dict[host.hostname] = problems
            host_problems_list.append({"hostname": host.hostname, "problems": problems})
        except Problem.DoesNotExist:
            pass

    results = {
        'sys': sys,
        'svc': svc,
        'host': host,
        'item_list': allhost,
        'host_problems_dict': host_problems_dict,
        'host_problems_list': host_problems_list,
        'cur_time_rng': time_rng
    }

    resp = render(request, "monitor/health-problems.html", results)
    resp.set_cookie("host_id", host_id)
    return resp


@login_required()
@permission_verify()
def problem(request, problem_id):
    problem = Problem.objects.get(id=problem_id)
    return render(request, "monitor/problem-detail.html", locals())


@login_required()
@permission_verify()
def notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id)
    return render(request, "monitor/notification-detail.html", locals())


@login_required()
@permission_verify()
def metric_overview_systems(request):
    refresh_time_rng(request)
    cur_time_rng = time_rng
    resp = render(request, "monitor/health-metric-overview.html", locals())
    resp.set_cookie("time-rng", cookie_time_rng)
    return resp


@login_required()
@permission_verify()
def metric_overview_services(request):
    refresh_time_rng(request)
    result = get_metric_all_service_data(request)
    resp = render(request, "monitor/health-metric-overview-services.html", result)
    resp.set_cookie("time-rng", cookie_time_rng)
    return resp


@login_required()
@permission_verify()
def metric_service_index_hosts(request, service_id):
    refresh_time_rng(request)
    result = get_metric_service_index_hosts_data(service_id)
    resp = render(request, "monitor/health-metric-service-hosts.html", result)
    resp.set_cookie("service_id", service_id)
    resp.set_cookie("time-rng", cookie_time_rng)
    return resp


@login_required()
@permission_verify()
def metric_index_hosts(request, system_id):
    refresh_time_rng(request)
    result = get_metric_index_hosts_data(system_id)  # 耗时
    resp = render(request, "monitor/health-metric-hosts.html", result)
    resp.set_cookie("system_id", system_id)
    resp.set_cookie("time-rng", cookie_time_rng)
    return resp


@login_required()
@permission_verify()
def metric_index_problems(request, host_id):
    refresh_time_rng(request)
    host = Host.objects.get(id=host_id)
    # todo test
    # find_plat, find_sys, find_svc, host = get_host_group_info(host_id)
    #
    cur_sys = None
    cur_svc = None
    system_id = request.COOKIES.get('system_id')
    service_id = request.COOKIES.get('service_id')
    #
    if request.GET.get("fr") == "wx":
        system_id = None
    if system_id and "-1" != system_id:
        cur_sys = ServiceSystem.objects.get(id=system_id)
    if service_id and "-1" != service_id:
        cur_svc = HostService.objects.get(id=service_id)

    url_get_items = "/monitor/health/getproblems/?hostid={}".format(host_id)
    result = {
        "host": host,
        "sys": cur_sys,
        "svc": cur_svc,
        "url_get_items": url_get_items,
        "cur_time_rng": time_rng
    }
    resp = render(request, "monitor/health-metric-problems.html", result)
    resp.set_cookie("host_id", host_id)
    resp.set_cookie("time-rng", cookie_time_rng)
    return resp


@login_required()
@permission_verify()
def metric_service_index_problems(request, host_id):
    refresh_time_rng(request, max_days=90)
    host = Host.objects.get(id=host_id)
    cur_svc = None
    service_id = request.COOKIES.get('service_id')
    if service_id and "-1" != service_id:
        cur_svc = HostService.objects.get(id=service_id)

    # if not cur_svc:
    #     return HttpResponseRedirect(reverse('metric_overview_systems'))
    url_get_items = "/monitor/health/getproblems/?hostid={}".format(host_id)
    result = {
        "host": host,
        "svc": cur_svc,
        "cur_time_rng": time_rng,
        "url_get_items": url_get_items
    }
    resp = render(request, "monitor/health-metric-problems.html", result)
    resp.set_cookie("host_id", host_id)
    resp.set_cookie("time-rng", cookie_time_rng)
    return resp
