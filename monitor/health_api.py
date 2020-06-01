#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import urllib
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify
from django.core import serializers
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse
from cmdb.models import Host, HostService, ServiceSystem, SystemGroup
from models import Problem, Metric, Instance, Item, Notification


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


def count_problems_met(instances=None, status=None):
    result = []
    try:
        if instances is None:
            problem_data = Problem.objects.filter(create_time__range=time_rng).extra(
                select={"create_time":
                            "DATE_FORMAT(CONVERT_TZ(`create_time`,'UTC','Asia/Shanghai'),'%%Y-%%m-%%d %%Hh')"}).values(
                'create_time')
        else:
            problem_data = Problem.objects.filter(item__instance__in=instances,
                                                  create_time__range=time_rng).extra(
                select={"create_time":
                            "DATE_FORMAT(CONVERT_TZ(`create_time`,'UTC','Asia/Shanghai'),'%%Y-%%m-%%d %%Hh')"}).values(
                'create_time')
        all_metric = Metric.objects.all()
        for met in all_metric:
            if status is None:
                result.append({'name': met.name.split('.')[-1],
                               'value': len(problem_data.filter(item__trigger__metric=met))})
            elif 0 == status:
                result.append({'name': met.name.split('.')[-1],
                               'value': len(problem_data.filter(item__trigger__metric=met,
                                                                status=0))})
    except Problem.DoesNotExist:
        pass
    else:
        pass

    result = sorted(result, key=lambda x: x['value'])
    return HttpResponse(json.dumps(result))


def count_problems_by_ins(instances=None):
    if instances is None:
        instances = Instance.objects.all()
    elif not instances:
        return HttpResponse(json.dumps([]))

    result = []
    try:
        problem_data = Problem.objects.filter(item__instance__in=instances,
                                              create_time__range=time_rng).extra(
            select={"create_time":
                        "DATE_FORMAT(CONVERT_TZ(`create_time`,'UTC','Asia/Shanghai'),'%%Y-%%m-%%d %%Hh')"}).values(
            'create_time').order_by('create_time').annotate(count=Count('create_time'))
        result.extend(problem_data)
    except Problem.DoesNotExist:
        print("problem does not exist")
    else:
        pass

    if result:
        result = sorted(result, key=lambda x: x['create_time'])
        t_st_str = result[0].get('create_time').split(' ')[0]
        t_st = datetime.datetime.strptime(t_st_str, '%Y-%m-%d')
        t_fn_str = result[len(result) - 1].get('create_time').split(' ')[0]
        t_fn = datetime.datetime.strptime(t_fn_str, '%Y-%m-%d')
        t_fn += datetime.timedelta(days=1)
        # 改用选定的st,fn
        t_st = datetime.datetime.strptime(time_rng[0], '%Y-%m-%d')
        t_fn = datetime.datetime.strptime(time_rng[1], '%Y-%m-%d')
    else:
        return HttpResponse(json.dumps([]))

    # 补零 ...
    day_strs = [d.get('create_time') for d in result]
    result_new = []
    for res in result:
        result_new.append({'count': res.get('count'), 'create_time': res.get('create_time')})

    i = 0
    t = t_st
    while True:
        t_str = t.strftime('%F %Hh')
        if t_str in day_strs:
            t += datetime.timedelta(hours=1)
            continue
        else:
            result_new.append({'count': 0, 'create_time': t_str})
            t += datetime.timedelta(hours=1)
            if t > t_fn:
                break
        i += 1
        if i > 3 * 365 * 24:
            break

    result_new = sorted(result_new, key=lambda x: x['create_time'])
    return HttpResponse(json.dumps(result_new))


def count_problems_by_ip(hosts):
    result = []
    ips = [host.ip for host in hosts]
    if ips:
        try:
            problem_data = Problem.objects.filter(ip__in=ips, create_time__range=time_rng).extra(
                select={"create_time":
                            "DATE_FORMAT(CONVERT_TZ(`create_time`,'UTC','Asia/Shanghai'),'%%Y-%%m-%%d %%Hh')"}).values(
                'create_time').order_by('create_time').annotate(count=Count('create_time'))
            result.extend(problem_data)
        except Problem.DoesNotExist:
            pass
        else:
            pass

    if result:
        result = sorted(result, key=lambda x: x['create_time'])
        t_st_str = result[0].get('create_time').split(' ')[0]
        t_st = datetime.datetime.strptime(t_st_str, '%Y-%m-%d')
        t_fn_str = result[len(result) - 1].get('create_time').split(' ')[0]
        t_fn = datetime.datetime.strptime(t_fn_str, '%Y-%m-%d')
        t_fn += datetime.timedelta(days=1)
        # 改用选定的st,fn
        t_st = datetime.datetime.strptime(time_rng[0], '%Y-%m-%d')
        t_fn = datetime.datetime.strptime(time_rng[1], '%Y-%m-%d')
    else:
        return HttpResponse(json.dumps([]))

    # 补零 ...
    day_strs = [d.get('create_time') for d in result]

    result_new = []
    for res in result:
        result_new.append({'count': res.get('count'), 'create_time': res.get('create_time')})

    i = 0
    t = t_st
    while True:
        t_str = t.strftime('%F %Hh')
        if t_str in day_strs:
            t += datetime.timedelta(hours=1)
            continue
        else:
            result_new.append({'count': 0, 'create_time': t_str})
            t += datetime.timedelta(hours=1)
            if t > t_fn:
                break
        i += 1
        if i > 3 * 365 * 24:
            break

    result_new = sorted(result_new, key=lambda x: x['create_time'])
    return HttpResponse(json.dumps(result_new))


@login_required()
@permission_verify()
def get_host_problems_data_cur(request, host_id):
    refresh_time_rng(request)
    host = Host.objects.get(id=host_id)
    host_ins = host.instanceList.all()
    return count_problems_met(instances=host_ins, status=0)


@login_required()
@permission_verify()
def get_host_problems_data_his(request, host_id):
    refresh_time_rng(request)
    host = Host.objects.get(id=host_id)
    host_ins = host.instanceList.all()
    return count_problems_met(instances=host_ins)


@login_required()
@permission_verify()
def get_host_problems_data(request, host_id):
    refresh_time_rng(request)
    host = Host.objects.get(id=host_id)
    allhosts = [host]
    return count_problems_by_ip(allhosts)


@login_required()
@permission_verify()
def get_service_problems_data_cur(request, service_id):
    refresh_time_rng(request)
    svc = HostService.objects.get(id=service_id)
    svc_ins = svc.instanceList.all()
    return count_problems_met(instances=svc_ins, status=0)


@login_required()
@permission_verify()
def get_service_problems_data_his(request, service_id):
    refresh_time_rng(request)
    svc = HostService.objects.get(id=service_id)
    svc_ins = svc.instanceList.all()
    return count_problems_met(instances=svc_ins)


@login_required()
@permission_verify()
def get_service_problems_data(request, service_id):
    refresh_time_rng(request)
    svc = HostService.objects.get(id=service_id)
    allhosts = svc.serverList.all()
    return count_problems_by_ip(allhosts)


@login_required()
@permission_verify()
def get_system_problems_data2(request, system_id):
    refresh_time_rng(request)
    sys = ServiceSystem.objects.get(id=system_id)
    allsvc = sys.serviceList.all()
    allhosts = []
    for svc in allsvc:
        hosts = svc.serverList.all()
        allhosts.extend(hosts)

    allhosts = list(set(allhosts))
    return count_problems_by_ip(allhosts)


@login_required()
@permission_verify()
def get_system_problems_data(request, system_id):
    refresh_time_rng(request)
    cur_sys = ServiceSystem.objects.get(id=system_id)
    sys_services = cur_sys.serviceList.all()
    sys_instances = []
    for svc in sys_services:
        svc_instances = svc.instanceList.all()
        sys_instances.extend(svc_instances)

    sys_instances = set(sys_instances)
    if not sys_instances:
        return HttpResponse(json.dumps([]))
    else:
        return count_problems_by_ins(instances=sys_instances)


@login_required()
@permission_verify()
def get_system_problems_data_cur(request, system_id):
    refresh_time_rng(request)
    cur_sys = ServiceSystem.objects.get(id=system_id)
    sys_services = cur_sys.serviceList.all()
    sys_instances = []
    for svc in sys_services:
        svc_instances = svc.instanceList.all()
        sys_instances.extend(svc_instances)

    sys_instances = set(sys_instances)
    if not sys_instances:
        return HttpResponse(json.dumps([]))
    else:
        return count_problems_met(instances=sys_instances, status=0)


@login_required()
@permission_verify()
def get_latest5_hosts(request):
    refresh_time_rng(request)
    plat_id = request.COOKIES.get('plat') or ""
    plat_id = urllib.unquote(plat_id)
    aria_controls_id = request.COOKIES.get('aria_controls') or ""
    aria_controls_id = urllib.unquote(aria_controls_id)
    if str(aria_controls_id).startswith('multiCollapse-'):
        aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
    else:
        aria_controls_id = ""
    system_id = request.GET.get('sysid', '')
    service_id = request.GET.get('svcid', '')
    host_id = request.GET.get('hostid', '')

    all_ins = []
    is_all = False
    if host_id:
        host = Host.objects.get(id=host_id)
        all_ins = host.instanceList.all()
    elif service_id:
        service = HostService.objects.get(id=service_id)
        all_ins = service.instanceList.all()
    elif system_id:
        system = ServiceSystem.objects.get(id=system_id)
        all_svc = system.serviceList.all()
        for svc in all_svc:
            all_ins.extend(svc.instanceList.all())
        all_ins = set(all_ins)
    elif aria_controls_id:
        all_ins = get_plat_instances(aria_controls_id=aria_controls_id, plat_id=plat_id)
    else:
        is_all = True

    if is_all:
        all_problems = Problem.objects.filter(create_time__range=time_rng, status=0)
    else:
        all_problems = Problem.objects.filter(item__instance__in=all_ins,
                                              create_time__range=time_rng, status=0)

    res = all_problems.values('ip', 'instance', 'name').order_by('-create_time')
    # res = all_problems.values('ip', 'instance', 'name').annotate(
    #     latest_date=Max('create_time')).order_by('-latest_date')

    res_list = []
    host = None
    for r in res:
        try:
            host = Host.objects.get(hostname=r['instance'])
        except Host.DoesNotExist:
            try:
                host = Host.objects.filter(ip=r['ip']).first()
            except Host.DoesNotExist:
                pass

        res_list.append(
            {
                'problem': {
                    'ip': r['ip'],
                    'instance': r['instance'],
                    'name': r.get('name') or ""
                },
                'host_id': host.id if host else "",
                'total': 1
            }
        )

    ip0 = []
    latest_res = []
    if host_id:
        latest_res = res_list[:20]
    else:
        for i in xrange(len(res_list)):
            res = res_list[i]
            try:
                cur_ip = res['problem']['ip']
                if cur_ip not in ip0:
                    latest_res.append(res)
                    ip0.append(cur_ip)
                if len(ip0) >= 20:
                    break
            except Exception:
                pass

    return HttpResponse(json.dumps(latest_res))


@login_required()
@permission_verify()
def get_system_problems_data_his(request, system_id):
    refresh_time_rng(request)
    cur_sys = ServiceSystem.objects.get(id=system_id)
    sys_services = cur_sys.serviceList.all()
    sys_instances = []
    for svc in sys_services:
        svc_instances = svc.instanceList.all()
        sys_instances.extend(svc_instances)

    sys_instances = set(sys_instances)
    return count_problems_met(instances=sys_instances)


@login_required()
@permission_verify()
def get_systems_problems_data(request):
    refresh_time_rng(request)
    allhosts = Host.objects.all()
    return count_problems_by_ip(allhosts)


@login_required()
@permission_verify()
def get_systems_problems_data_histo(request):
    refresh_time_rng(request)
    plat_id = request.COOKIES.get('plat') or ""
    plat_id = urllib.unquote(plat_id)
    aria_controls_id = request.COOKIES.get('aria_controls') or ""
    aria_controls_id = urllib.unquote(aria_controls_id)
    if str(aria_controls_id).startswith('multiCollapse-'):
        aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
    else:
        aria_controls_id = ""

    if aria_controls_id or plat_id:
        return count_problems_by_ins(instances=get_plat_instances(aria_controls_id=aria_controls_id,
                                                                  plat_id=plat_id))
    else:
        return count_problems_by_ins()


def get_plat_instances(plat_id=None, aria_controls_id=None):
    if not plat_id and not aria_controls_id:
        return Instance.objects.all()

    plat_instances = []
    if aria_controls_id:
        plat_systems = SystemGroup.objects.get(id=int(aria_controls_id)).systemList.all()
    elif plat_id:
        plat_systems = SystemGroup.objects.get(id=int(plat_id)).systemList.all()
    for p_sys in plat_systems:
        sys_instances = []
        sys_services = p_sys.serviceList.all()
        for svc in sys_services:
            svc_instances = svc.instanceList.all()
            sys_instances.extend(svc_instances)
        plat_instances.extend(sys_instances)
    plat_instances = list(set(plat_instances))
    return plat_instances


@login_required()
@permission_verify()
def get_systems_problems_data_cur(request):
    refresh_time_rng(request)
    plat_id = request.COOKIES.get('plat') or ""
    plat_id = urllib.unquote(plat_id)
    aria_controls_id = request.COOKIES.get('aria_controls') or ""
    aria_controls_id = urllib.unquote(aria_controls_id)
    if str(aria_controls_id).startswith('multiCollapse-'):
        aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
    else:
        aria_controls_id = ""

    plat_instances = None
    if aria_controls_id:
        plat_instances = get_plat_instances(aria_controls_id=aria_controls_id, plat_id=plat_id)
    return count_problems_met(instances=plat_instances, status=0)


@login_required()
@permission_verify()
def get_systems_problems_data_his(request):
    refresh_time_rng(request)
    # return count_problems_met()
    plat_id = request.COOKIES.get('plat') or ""
    plat_id = urllib.unquote(plat_id)
    aria_controls_id = request.COOKIES.get('aria_controls') or ""
    aria_controls_id = urllib.unquote(aria_controls_id)
    if str(aria_controls_id).startswith('multiCollapse-'):
        aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
    else:
        aria_controls_id = ""

    plat_instances = None
    if aria_controls_id:
        plat_instances = get_plat_instances(aria_controls_id=aria_controls_id, plat_id=plat_id)
    return count_problems_met(instances=plat_instances)


def get_all_system_data(allsys, allgrp):
    # todo get_all_*_data
    allsys_data = {}
    g_allsys = list(set(allsys))

    grp_info = {}
    for grp in allgrp:
        grp_systems = grp.systemList.all()
        grp_info.setdefault(grp.name, {})['systems'] = grp_systems
        grp_info.setdefault(grp.name, {})['services'] = []
        grp_info.setdefault(grp.name, {})['hosts'] = []
        grp_info.setdefault(grp.name, {})['problems'] = []

    for sys in g_allsys:
        sys_hosts = []
        sys_services = sys.serviceList.all()

        for svc in sys_services:
            svc_hosts = svc.serverList.all()
            sys_hosts.extend(svc_hosts)

        sys_hosts = list(set(sys_hosts))
        sys_problems = []
        for host in sys_hosts:
            try:
                problems = Problem.objects.filter(ip=host.ip,
                                                  status=0,
                                                  create_time__range=time_rng)
                sys_problems.extend(problems)
            except Problem.DoesNotExist:
                pass

        for grp in grp_info:
            if sys in grp_info[grp]['systems']:
                grp_info[grp]['services'].extend(sys_services)
                grp_info[grp]['hosts'].extend(sys_hosts)
                grp_info[grp]['problems'].extend(sys_problems)

        data = {
            'total_services': len(sys_services), 'total_problems': len(sys_problems),
            'low_problems': len([p for p in sys_problems if p.severity == 1]),
            'med_problems': len([p for p in sys_problems if p.severity == 2]),
            'high_problems': len([p for p in sys_problems if p.severity == 3])
        }
        allsys_data[sys.name] = data

    # 已汇总，去重
    for grp in grp_info:
        t = grp_info[grp]['services']
        grp_info[grp]['services'] = len(set(t))
        t = grp_info[grp]['hosts']
        grp_info[grp]['hosts'] = len(set(t))
        t = grp_info[grp]['problems']
        grp_info[grp]['problems'] = len(set(t))

    result = {
        "allsys": g_allsys,
        "allsys_data": allsys_data,
        "grp_info": grp_info,
        "cur_time_rng": time_rng
    }

    return result


def get_all_service_data(sys_id=None):
    if sys_id:
        cur_sys = ServiceSystem.objects.get(id=sys_id)
        allsvc = cur_sys.serviceList.all()
    else:
        cur_sys = None
        allsvc = HostService.objects.all()

    allsvc_data = {}
    for svc in allsvc:
        svc_hosts = svc.serverList.all()
        svc_problems = []
        for host in svc_hosts:
            try:
                problems = Problem.objects.filter(ip=host.ip,
                                                  status=0,
                                                  create_time__range=time_rng)
                svc_problems.extend(problems)
            except Problem.DoesNotExist:
                pass

        data = {
            'svc': svc,
            'total_hosts': len(svc_hosts), 'total_problems': len(svc_problems),
            'low_problems': len([p for p in svc_problems if p.severity == 1]),
            'med_problems': len([p for p in svc_problems if p.severity == 2]),
            'high_problems': len([p for p in svc_problems if p.severity == 3])
        }
        allsvc_data[svc.name] = data

    # 先总后重
    sorted_allsvc_name = sorted(sorted(allsvc_data,
                                       key=lambda k: allsvc_data[k]['high_problems'],
                                       reverse=True),
                                key=lambda k: allsvc_data[k]['total_problems'],
                                reverse=True)
    sorted_allsvc = [allsvc_data[name]['svc'] for name in sorted_allsvc_name]

    result = {
        "sorted_allsvc": sorted_allsvc,
        "allsvc_data": allsvc_data,
        "cur_time_rng": time_rng,
        "sys": cur_sys
    }
    return result


def get_all_host_data(service_id=None):
    allsvc_hosts = []
    allsvc = HostService.objects.all()
    for svc in allsvc:
        allsvc_hosts.extend(svc.serverList.all())

    allsvc_hosts = list(set(allsvc_hosts))
    if service_id:
        svc = HostService.objects.get(id=service_id)
        allhost = svc.serverList.all()
    else:
        svc = None
        allhost = allsvc_hosts

    allhost_data = {}
    for host in allhost:
        is_attached = 0
        if host in allsvc_hosts:
            is_attached = 1

        svc_problems = []
        try:
            svc_problems = Problem.objects.filter(ip=host.ip, status=0, create_time__range=time_rng)
        except Problem.DoesNotExist:
            pass

        data = {
            'host': host,
            'is_attached': is_attached,
            'total_problems': len(svc_problems),
            'low_problems': len([p for p in svc_problems if p.severity == 1]),
            'med_problems': len([p for p in svc_problems if p.severity == 2]),
            'high_problems': len([p for p in svc_problems if p.severity == 3])
        }
        allhost_data[host.hostname] = data

    # 先总后重
    sorted_allhost_name = sorted(sorted(allhost_data,
                                        key=lambda k: allhost_data[k]['high_problems'],
                                        reverse=True),
                                 key=lambda k: allhost_data[k]['total_problems'],
                                 reverse=True)
    sorted_allhost = [allhost_data[name]['host'] for name in sorted_allhost_name]
    result = {
        "svc": svc,
        "sorted_allhost": sorted_allhost,
        "allhost_data": allhost_data,
        "cur_time_rng": time_rng
    }
    return result


def get_overview_systems_data():
    allsys = ServiceSystem.objects.all()
    allsysgroup = SystemGroup.objects.all()
    allsysdata = get_all_system_data(allsys, allsysgroup)
    allgrpdata = {}
    for grp in allsysgroup:
        allgrpdata.setdefault(grp.name, {"systems": grp.systemList.all(), "systemgroup": grp})
    return {
        "allsysdata": allsysdata,
        "allgrpdata": allgrpdata,
        "cur_time_rng": time_rng
    }


@login_required()
@permission_verify()
def get_problems_data(request):
    draw = int(request.GET.get('draw'))
    start = int(request.GET.get('start'))
    length = int(request.GET.get('length'))
    host_id = request.GET.get('hostid')
    host_id = int(host_id) if host_id else None
    s_search = request.GET.get('s_search') or ""
    order_col = request.GET.get('order[0][column]')
    order_col_name = request.GET.get('columns[{}][data]'.format(order_col))
    order_type = '' if request.GET.get('order[0][dir]') == 'asc' else '-'
    #
    refresh_time_rng(request)
    kw = {"create_time__range": time_rng}
    if not host_id:
        plat_id = request.COOKIES.get('plat') or ""
        plat_id = urllib.unquote(plat_id)
        aria_controls_id = request.COOKIES.get('aria_controls') or ""
        aria_controls_id = urllib.unquote(aria_controls_id)
        if str(aria_controls_id).startswith('multiCollapse-'):
            aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
        else:
            aria_controls_id = ""

        all_ins = []
        is_all = False
        if aria_controls_id:
            all_ins = get_plat_instances(aria_controls_id=aria_controls_id)
        elif plat_id:
            all_ins = get_plat_instances(plat_id=plat_id)
        else:
            is_all = True

        if not is_all:
            kw.update({"item__instance__in": all_ins})
    else:
        host = Host.objects.get(id=host_id)
        host_ins = host.instanceList.all()
        kw.update({"item__instance__in": host_ins})

    count = 0
    if s_search:
        count = Problem.objects.filter(**kw).filter(
            Q(ip__icontains=s_search)
            | Q(instance__icontains=s_search)
            | Q(name__icontains=s_search)
            | Q(expr__icontains=s_search)).count()
        filtered_problems = Problem.objects.filter(**kw).filter(
            Q(ip__icontains=s_search)
            | Q(instance__icontains=s_search)
            | Q(name__icontains=s_search)
            | Q(expr__icontains=s_search)
        ).order_by('{}{}'.format(order_type, order_col_name))[start:start + length]
    else:
        count = Problem.objects.filter(**kw).count()
        filtered_problems = Problem.objects.filter(**kw).order_by(
            '{}{}'.format(order_type, order_col_name))[start:start + length]

    if filtered_problems:
        data = [{"instance": p.instance,
                 "severity": p.severity,
                 "status": p.status,
                 "source": p.source,
                 "desc": p.desc,
                 "name": p.name,
                 "id": p.id,
                 "ip": p.ip,
                 "expr": p.expr,
                 "create_time": p.create_time,
                 "update_time": p.update_time,
                 } for p in filtered_problems]
    else:
        data = []

    dic = {
        'code': 200,
        'draw': draw,
        'recordsFiltered': count,
        'recordsTotal': count,
        'data': data
    }
    return JsonResponse(dic)


def get_plat_name(request):
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
    return plat_name


@login_required()
@permission_verify()
def get_notifications_data(request):
    draw = int(request.GET.get('draw'))
    start = int(request.GET.get('start'))
    length = int(request.GET.get('length'))
    host_id = request.GET.get('hostid')
    host_id = int(host_id) if host_id else None
    s_search = request.GET.get('s_search') or ""
    order_col = request.GET.get('order[0][column]')
    order_col_name = request.GET.get('columns[{}][data]'.format(order_col))
    order_type = '' if request.GET.get('order[0][dir]') == 'asc' else '-'
    #
    refresh_time_rng(request)
    kw = {"create_time__range": time_rng}
    if not host_id:
        plat_id = request.COOKIES.get('plat') or ""
        plat_id = urllib.unquote(plat_id)
        aria_controls_id = request.COOKIES.get('aria_controls') or ""
        aria_controls_id = urllib.unquote(aria_controls_id)
        if str(aria_controls_id).startswith('multiCollapse-'):
            aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
        else:
            aria_controls_id = ""

        all_ins = []
        is_all = False
        if aria_controls_id:
            all_ins = get_plat_instances(aria_controls_id=aria_controls_id)
        elif plat_id:
            all_ins = get_plat_instances(plat_id=plat_id)
        else:
            is_all = True

        if not is_all:
            all_ip = set([ins.ip for ins in all_ins])
            kw.update({"ip__in": all_ip})
    else:
        host = Host.objects.get(id=host_id)
        host_ins = host.instanceList.all()
        all_ip = set([ins.ip for ins in host_ins])
        kw.update({"ip__in": all_ip})

    count = 0
    if s_search:
        count = Notification.objects.filter(**kw).filter(
            Q(ip__icontains=s_search)
            | Q(instance__icontains=s_search)
            | Q(name__icontains=s_search)
            | Q(expr__icontains=s_search)
            | Q(receivers__contains=s_search)).count()
        filtered_items = Notification.objects.filter(**kw).filter(
            Q(ip__icontains=s_search)
            | Q(instance__icontains=s_search)
            | Q(name__icontains=s_search)
            | Q(expr__icontains=s_search)
            | Q(receivers__contains=s_search)
        ).order_by('{}{}'.format(order_type, order_col_name))[start:start + length]
    else:
        count = Notification.objects.filter(**kw).count()
        filtered_items = Notification.objects.filter(**kw).order_by(
            '{}{}'.format(order_type, order_col_name))[start:start + length]

    if filtered_items:
        data = [{"instance": p.instance,
                 "severity": p.severity,
                 "status": p.status,
                 "source": p.source,
                 "desc": p.desc,
                 "name": p.name,
                 "id": p.id,
                 "ip": p.ip,
                 "receivers": p.receivers,
                 "expr": p.expr,
                 "create_time": p.create_time,
                 } for p in filtered_items]
    else:
        data = []

    dic = {
        'code': 200,
        'draw': draw,
        'recordsFiltered': count,
        'recordsTotal': count,
        'data': data
    }
    return JsonResponse(dic)


def get_metric_all_system_data2(allsys, allgrp, allmetric):
    allsys_data = {}
    g_allsys = set(allsys)

    grp_info = {}
    for grp in allgrp:
        grp_systems = grp.systemList.all()
        grp_info.setdefault(grp.name, {})['systems'] = grp_systems
        grp_info.setdefault(grp.name, {})['services'] = []
        grp_info.setdefault(grp.name, {})['instances'] = []
        grp_info.setdefault(grp.name, {})['problems'] = []

    for sys in g_allsys:
        sys_instances = []
        sys_services = sys.serviceList.all()
        for svc in sys_services:
            svc_instances = svc.instanceList.all()
            sys_instances.extend(svc_instances)

        sys_instances = list(set(sys_instances))  # 当前系统的所有实例
        sys_items = Item.objects.filter(instance__in=sys_instances)
        sys_problems = Problem.objects.filter(item__in=sys_items,
                                              status=0,
                                              create_time__range=time_rng)
        sys_data = {}
        for metric in allmetric:
            # 当前系统 各指标项的问题
            metric_items = Item.objects.filter(instance__in=sys_instances, trigger__metric=metric)
            metric_problems = Problem.objects.filter(item__in=metric_items,
                                                     status=0,
                                                     create_time__range=time_rng)
            sys_data.setdefault('metric_problems', {}).setdefault(
                metric.name, {
                    'p3': len([p for p in metric_problems if 3 == p.severity]),
                    'p2': len([p for p in metric_problems if 2 == p.severity]),
                    'p1': len([p for p in metric_problems if 1 == p.severity])
                }
            )

        # 当前系统的问题 汇总至平台
        for grp in grp_info:
            if sys in grp_info[grp]['systems']:
                grp_info[grp]['services'].extend(
                    serializers.serialize("json", sys_services))  # 平台所有服务
                grp_info[grp]['instances'].extend(
                    serializers.serialize("json", sys_instances))  # 平台所有实例
                grp_info[grp]['problems'].extend(
                    serializers.serialize("json", sys_problems))  # 平台所有问题

        sys_data['total_services'] = len(sys_services)  # 当前系统的服务数
        sys_data['total_instances'] = len(sys_instances)  # 当前系统的实例数
        sys_data['total_items'] = len(sys_items)  # 当前系统的监控项总数
        sys_data['total_problems'] = len(sys_problems)  # 当前系统的问题数 ...
        sys_data['caution_problems'] = len(sys_problems.filter(severity__gte=3))  # 当前系统的问题数 ...
        sys_data['p1'] = len(sys_problems.filter(severity=1))
        sys_data['p2'] = len(sys_problems.filter(severity=2))
        sys_data['p3'] = len(sys_problems.filter(severity=3))
        allsys_data[sys.name] = sys_data

    # 已汇总，去重
    for grp in grp_info:
        grp_info[grp]['systems'] = serializers.serialize("json", grp_info[grp]['systems'])
        t = grp_info[grp]['services']
        grp_info[grp]['services'] = len(set(t))
        t = grp_info[grp]['instances']
        grp_info[grp]['instances'] = len(set(t))
        t = grp_info[grp]['problems']
        grp_info[grp]['problems'] = len(set(t))

    result = {
        "grp_info": grp_info,
        "allsys": serializers.serialize("json", g_allsys),
        "allsys_data": allsys_data,
        "cur_time_rng": time_rng
    }
    return result


def get_metric_all_grp_info(allsys, allgrp):
    grp_info = {}

    for grp in allgrp:
        grp_systems = grp.systemList.all()
        if grp_systems:
            # 平台未关联系统，将不加入此平台的名称及systems信息
            grp_info.setdefault(grp.name, {})['systems'] = grp_systems

    for sys in allsys:
        sys_instances = []
        sys_services = sys.serviceList.all()
        for svc in sys_services:
            svc_instances = svc.instanceList.all()
            sys_instances.extend(svc_instances)
        for gn in grp_info:
            if sys in grp_info[gn]['systems']:
                grp_info[gn].setdefault('instances', []).extend(sys_instances)

    for gn in grp_info:
        grp_instances = set(grp_info[gn]['instances'])
        grp_info[gn]['problems'] = len(Problem.objects.filter(create_time__range=time_rng,
                                                              item__instance__in=grp_instances,
                                                              status=0))
    result = {
        "grp_info": grp_info,
        "cur_time_rng": time_rng
    }

    return result


def get_metric_service_index_hosts_data(cur_svc_id):
    cur_svc = HostService.objects.get(id=cur_svc_id)
    svc_instances = cur_svc.instanceList.all()
    sorted_allhost_name, sorted_allhost, allhost_metric_data = proc_metric_hosts_data(svc_instances)
    return {
        "svc": cur_svc,
        "sorted_allhost": sorted_allhost,
        "allhost_metric_data": allhost_metric_data,
        "cur_time_rng": time_rng
    }


def proc_metric_hosts_data(instances):
    # 1. 先都初始为0
    allmetric = Metric.objects.all()
    allhost = []
    for ins in instances:
        ins_hosts = ins.host_set.all()
        allhost.extend(ins_hosts)

    allhost = list(set(allhost))
    sys_items = Item.objects.filter(instance__in=instances)
    allhost_metric_data = {}
    for host in allhost:
        host_data = {
            "host": host,
            "total_items": 0,
            "total_problems": 0,
            "caution_problems": 0,
            "p1": 0,
            "p2": 0,
            "p3": 0,
        }

        for metric in allmetric:
            host_data.setdefault('metric_problems', {}).setdefault(
                metric.name, {
                    'p3': 0,
                    'p2': 0,
                    'p1': 0
                }
            )

        allhost_metric_data.setdefault(host.hostname, host_data)

    # 2. 针对有问题的主机改写
    allhost_problems = Problem.objects.filter(item__in=sys_items,
                                              status=0,
                                              create_time__range=time_rng)

    all_problem_host = Host.objects.filter(
        instanceList__instance_itemList__item_problemList__in=allhost_problems)

    for host in all_problem_host:
        host_problems = allhost_problems.filter(item__instance__host=host)
        host_instance_items = sys_items.filter(instance__host=host)
        host_data = {
            "host": host,
            "total_items": len(host_instance_items),
            "total_problems": len(host_problems),
            "caution_problems": len(host_problems.filter(severity__gte=3)),
            "p1": len(host_problems.filter(severity=1)),
            "p2": len(host_problems.filter(severity=2)),
            "p3": len(host_problems.filter(severity=3)),
        }

        for metric in allmetric:
            metric_problems = host_problems.filter(item__trigger__metric=metric)
            host_data.setdefault('metric_problems', {}).setdefault(
                metric.name, {
                    'p3': len([p for p in metric_problems if 3 == p.severity]),
                    'p2': len([p for p in metric_problems if 2 == p.severity]),
                    'p1': len([p for p in metric_problems if 1 == p.severity])
                }
            )

        allhost_metric_data[host.hostname] = host_data

    # 先重后总
    sorted_allhost_name = sorted(sorted(allhost_metric_data,
                                        key=lambda k: allhost_metric_data[k]['total_problems'],
                                        reverse=True),
                                 key=lambda k: allhost_metric_data[k]['caution_problems'],
                                 reverse=True)
    sorted_allhost = [allhost_metric_data[name]['host'] for name in sorted_allhost_name]
    return sorted_allhost_name, sorted_allhost, allhost_metric_data


def get_metric_index_hosts_data(cur_sys_id):
    cur_sys = ServiceSystem.objects.get(id=cur_sys_id)
    sys_services = cur_sys.serviceList.all()
    sys_instances = []
    for svc in sys_services:
        svc_instances = svc.instanceList.all()
        sys_instances.extend(svc_instances)
    sorted_allhost_name, sorted_allhost, allhost_metric_data = proc_metric_hosts_data(sys_instances)
    return {
        "sys": cur_sys,
        "sorted_allhost": sorted_allhost,
        "allhost_metric_data": allhost_metric_data,
        "cur_time_rng": time_rng
    }


@login_required()
@permission_verify()
def get_metric_hosts_pie_data(request, system_id):
    refresh_time_rng(request)
    cur_sys = ServiceSystem.objects.get(id=system_id)
    # 须从实例反查host、item，再筛选出各指标数据
    sys_services = cur_sys.serviceList.all()
    sys_instances = []
    for svc in sys_services:
        svc_instances = svc.instanceList.all()
        sys_instances.extend(svc_instances)

    allhost = []
    for ins in sys_instances:
        ins_hosts = ins.host_set.all()
        allhost.extend(ins_hosts)

    allhost = list(set(allhost))
    sys_items = Item.objects.filter(instance__in=sys_instances)
    host_pie_data = []
    for host in allhost:
        host_instance_items = sys_items.filter(instance__host=host)
        host_problems = Problem.objects.filter(item__in=host_instance_items,
                                               status=0,
                                               create_time__range=time_rng)
        host_pie_data.append({"name": host.hostname, "value": len(host_problems)})

    host_pie_data.sort(key=lambda x: x['value'], reverse=True)
    resp = {
        "pie_data": host_pie_data,
        "cur_time_rng": time_rng
    }
    return HttpResponse(json.dumps(resp))


@login_required()
@permission_verify()
def get_metric_severity_pie_data(request, s_id):
    refresh_time_rng(request)
    s_item = Host.objects.get(id=s_id)
    all_problems = Problem.objects.filter(item__instance__host=s_item,
                                          create_time__range=time_rng, status=0)
    res = all_problems.values('severity').annotate(total=Count('severity')).order_by('total')
    host_pie_data = []
    severity_names = {"0": u"已恢复", "1": u"低", "2": u"中", "3": u"高", "4": u"危"}
    for r in res:
        host_pie_data.append({"name": severity_names.get(str(r['severity'])),
                              "value": r['total']})

    host_pie_data.sort(key=lambda x: x['value'], reverse=True)
    resp = {
        "pie_data": host_pie_data[:4],
        "cur_time_rng": time_rng
    }
    return HttpResponse(json.dumps(resp))


@login_required()
@permission_verify()
def get_metric_service_hosts_pie_data(request, service_id):
    refresh_time_rng(request)
    cur_svc = HostService.objects.get(id=service_id)
    svc_instances = cur_svc.instanceList.all()
    allhost = []
    for ins in svc_instances:
        ins_hosts = ins.host_set.all()
        allhost.extend(ins_hosts)

    allhost = list(set(allhost))
    svc_items = Item.objects.filter(instance__in=svc_instances)
    host_pie_data = []
    for host in allhost:
        host_instance_items = svc_items.filter(instance__host=host)
        host_problems = Problem.objects.filter(item__in=host_instance_items,
                                               status=0,
                                               create_time__range=time_rng)
        host_pie_data.append({"name": host.hostname, "value": len(host_problems)})

    host_pie_data.sort(key=lambda x: x['value'], reverse=True)

    resp = {
        "pie_data": host_pie_data,
        "cur_time_rng": time_rng
    }
    return HttpResponse(json.dumps(resp))


@login_required()
@permission_verify()
def get_metric_overview_page_tags(request):
    refresh_time_rng(request)
    plat_id = request.COOKIES.get('plat') or ""
    plat_id = urllib.unquote(plat_id)
    aria_controls_id = request.COOKIES.get('aria_controls') or ""
    aria_controls_id = urllib.unquote(aria_controls_id)
    if not str(aria_controls_id).startswith('multiCollapse-'):
        aria_controls_id = ""

    if plat_id and not aria_controls_id:
        all_sys_group = SystemGroup.objects.filter(id=int(plat_id))
    else:
        if request.user.username == "admin":
            all_sys_group = SystemGroup.objects.all()
        else:
            exclude_names = ['X', 'ALL', u'所有', u'所有平台', u'全部']
            all_sys_group = SystemGroup.objects.exclude(name__in=exclude_names)

    # if str(aria_controls_id).startswith('multiCollapse-'):
    #     aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
    #     all_sys_group = SystemGroup.objects.filter(id=aria_controls_id)
    # elif plat_id:
    #     all_sys_group = SystemGroup.objects.filter(name=plat_id)
    # else:
    #     all_sys_group = SystemGroup.objects.all()

    # all_sys_group = SystemGroup.objects.all()
    all_sys = ServiceSystem.objects.all()
    all_sys_data = get_metric_all_grp_info(all_sys, all_sys_group)
    all_grp_html = []
    plat_pie_data = [{'name': g, 'value': v['problems']} for g, v in all_sys_data['grp_info'].items()]
    plat_pie_data.sort(key=lambda x: x['value'], reverse=True)
    for grp_data in plat_pie_data:
        grp_name = grp_data['name']
        show_grp_name = grp_name
        if grp_name in ['X', 'ALL', u'所有', u'所有平台', u'全部']:
            if request.user.username != "admin":
                continue
            else:
                # show_grp_name = '<i class="fa fa-bullseye" aria-hidden="true"></i>'
                show_grp_name = '<i class="fa fa-globe" aria-hidden="true"></i>'
        grp = SystemGroup.objects.get(name=grp_name)
        n_problem = grp_data['value']
        cur_grphtml = """
            <button class="btn btn-primary" type="button" data-toggle="collapse"
                data-target="#multiCollapse-{grp_id}"
                aria-expanded="false"
                aria-controls="multiCollapse-{grp_id}">
                {grp_name}
                <span style="color: #f8ff62">({n_problem})</span>
            </button>""".format(grp_id=grp.id, grp_name=show_grp_name, n_problem=n_problem)
        if grp_name in ['X', 'ALL', u'所有', u'所有平台', u'全部']:
            all_grp_html.insert(0, cur_grphtml)
        else:
            all_grp_html.append(cur_grphtml)
    resp = {
        'pie_data': plat_pie_data,
        'allgrphtml': all_grp_html
    }
    return HttpResponse(json.dumps(resp))


@login_required()
@permission_verify()
def api_get_metric_overview_systems_data(request):
    refresh_time_rng(request)
    res = get_metric_overview_systems_data()
    resp = HttpResponse(json.dumps(res))
    return resp


def get_metric_overview_systems_data():
    allsysgroup = SystemGroup.objects.all()  # 平台
    allsys = ServiceSystem.objects.all()  # 系统
    allmetric = Metric.objects.all()  # 按每个系统均列出所有已定义的指标
    allsysdata = get_metric_all_system_data2(allsys, allsysgroup, allmetric)
    allgrpdata = {}
    for grp in allsysgroup:
        allgrpdata.setdefault(grp.name,
                              {"systems": serializers.serialize("json", grp.systemList.all()),
                               "metrics": serializers.serialize("json", allmetric)
                               })
    for grp in allsysgroup:
        allgrpdata[grp.name]["systemgroup"] = {"name": grp.name, "id": grp.id}
    resp = {
        "allsysdata": allsysdata,
        "allgrpdata": allgrpdata,
        "cur_time_rng": time_rng
    }
    return resp


def get_metric_all_service_data(request, sys_id=None):
    if sys_id:
        cur_sys = ServiceSystem.objects.get(id=sys_id)
        allsvc = cur_sys.serviceList.all()
    else:
        cur_sys = None
        allsvc = HostService.objects.all()

    allmetric = Metric.objects.all()
    allsvc_data = {}

    for svc in allsvc:
        if str(svc.name).lower() == "all":
            if "admin" != request.user.username:
                continue
        svc_data = {}
        svc_instances = svc.instanceList.all()
        svc_items = Item.objects.filter(instance__in=svc_instances)
        svc_problems = Problem.objects.filter(item__in=svc_items,
                                              status=0,
                                              create_time__range=time_rng)
        for metric in allmetric:
            metric_items = Item.objects.filter(instance__in=svc_instances, trigger__metric=metric)
            metric_problems = Problem.objects.filter(item__in=metric_items,
                                                     status=0,
                                                     create_time__range=time_rng)

            svc_data.setdefault('metric_problems', {}).setdefault(
                metric.name, {
                    'p3': len([p for p in metric_problems if 3 == p.severity]),
                    'p2': len([p for p in metric_problems if 2 == p.severity]),
                    'p1': len([p for p in metric_problems if 1 == p.severity])
                }
            )

        svc_data['svc'] = svc
        svc_data['total_instances'] = len(svc_instances)
        svc_data['total_items'] = len(svc_items)
        svc_data['total_problems'] = len(svc_problems)
        svc_data['caution_problems'] = len(svc_problems.filter(severity__gte=3))
        svc_data['p1'] = len(svc_problems.filter(severity=1))
        svc_data['p2'] = len(svc_problems.filter(severity=2))
        svc_data['p3'] = len(svc_problems.filter(severity=3))
        allsvc_data[svc.name] = svc_data

    # 先按严重数，再按总数
    # sorted_allsvc_name = sorted(sorted(allsvc_data,
    #                                    key=lambda k: allsvc_data[k]['total_problems'],
    #                                    reverse=True),
    #                             key=lambda k: allsvc_data[k]['caution_problems'],
    #                             reverse=True)

    # 先按总数，再按名称
    sorted_allsvc_name = sorted(sorted(allsvc_data, reverse=False),
                                key=lambda k: allsvc_data[k]['total_problems'],
                                reverse=True)

    sorted_allsvc = [allsvc_data[name]['svc'] for name in sorted_allsvc_name]
    result = {
        "sorted_allsvc": sorted_allsvc,
        "allsvc_data": allsvc_data,
        "cur_time_rng": time_rng,
        "sys": cur_sys
    }
    return result


def get_host_group_info(host_id):
    find_plat, find_sys, find_svc, host = [None, None, None, None]
    host = Host.objects.get(id=host_id)
    if not host:
        return find_plat, find_sys, find_svc, host

    find_svc = HostService.objects.filter(
        serverList__id=host_id).exclude(name="All").first()

    if not find_svc:
        find_svc = HostService.objects.get(name="All")

    find_sys = None
    find_plat = None
    if find_svc:
        find_sys = ServiceSystem.objects.filter(serviceList__id=find_svc.id).first()
        find_plat = SystemGroup.objects.filter(systemList__id=find_sys.id).first()

    # return {"result": [find_plat, find_sys, find_svc, host], "status": 1}
    return find_plat, find_sys, find_svc, host
