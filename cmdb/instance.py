#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import sys
import urllib
from datetime import datetime

from accounts.permission import permission_verify
from cmdb.api import get_object
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, render
from cmdb.forms import InstanceForm
from cmdb.models import Host
from monitor.health_api import get_plat_name, get_plat_instances
from monitor.models import Instance
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import JsonResponse


try:
    reload(sys)  # Python 2
    sys.setdefaultencoding('utf8')
except NameError:
    pass  # Python 3


@login_required()
@permission_verify()
def get_instances_data(request):
    draw = int(request.GET.get('draw'))
    start = int(request.GET.get('start'))
    length = int(request.GET.get('length'))
    s_search = request.GET.get('s_search') or ""
    order_col = request.GET.get('order[0][column]')
    order_col_name = request.GET.get('columns[{}][data]'.format(order_col))
    order_type = '' if request.GET.get('order[0][dir]') == 'asc' else '-'
    count = 0
    host_id = request.GET.get('hostid')
    host_id = int(host_id) if host_id else None
    filtered_items = []
    all_ids = []
    all_ins = []
    is_all = False
    kw = {}
    if not host_id:
        plat_id = request.COOKIES.get('plat') or ""
        plat_id = urllib.unquote(plat_id)
        aria_controls_id = request.COOKIES.get('aria_controls') or ""
        aria_controls_id = urllib.unquote(aria_controls_id)
        if str(aria_controls_id).startswith('multiCollapse-'):
            aria_controls_id = int(str(aria_controls_id).replace('multiCollapse-', ''))
        else:
            aria_controls_id = ""

        if aria_controls_id:
            all_ins = get_plat_instances(aria_controls_id=aria_controls_id)
        elif plat_id:
            all_ins = get_plat_instances(plat_id=plat_id)
        else:
            is_all = True
    else:
        host = Host.objects.get(id=host_id)
        all_ins = host.instanceList.all()

    if not is_all:
        all_ids = [ins.id for ins in all_ins]
        kw.update({"id__in": all_ids})

    if s_search:
        count = Instance.objects.filter(**kw).filter(
            Q(ip__icontains=s_search)
            | Q(name__icontains=s_search)
            | Q(name2__icontains=s_search)
        ).count()
        filtered_items = Instance.objects.filter(**kw).filter(
            Q(ip__icontains=s_search)
            | Q(name__icontains=s_search)
            | Q(name2__icontains=s_search)
        ).order_by('{}{}'.format(order_type, order_col_name))[start:start + length]
    else:
        count = Instance.objects.filter(**kw).count()
        filtered_items = Instance.objects.filter(**kw).order_by(
            '{}{}'.format(order_type, order_col_name))[start:start + length]

    if filtered_items:
        data = [{"id": p.id,
                 "name": p.name,
                 "name2": p.name2,
                 "update_time": p.update_time,
                 "ip": p.ip} for p in filtered_items]
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


@login_required()
@permission_verify()
def instance(request):
    url_get_items = '/cmdb/instance/getinstances/'
    plat_name = get_plat_name(request)
    return render(request, 'cmdb/instance.html', locals())


@login_required()
@permission_verify()
def instance_add(request):
    if request.method == "POST":
        a_form = InstanceForm(request.POST)
        if a_form.is_valid():
            a_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        return render(request, "cmdb/instance_add.html", locals())
    else:
        display_control = "none"
        a_form = InstanceForm()
        return render(request, "cmdb/instance_add.html", locals())


@login_required()
@permission_verify()
def instance_del(request):
    if 'GET' == request.method:
        instance_id = request.GET.get('id', '')
        if instance_id:
            Instance.objects.filter(id=instance_id).delete()
        return HttpResponseRedirect(reverse('instance_index'))

    if 'POST' == request.method:
        instance_batch = request.GET.get('arg', '')
        instance_id_all = str(request.POST.get('instance_id_all', ''))

        if instance_batch:
            for instance_id in instance_id_all.split(','):
                instance_instance = get_object(Instance, id=instance_id)
                instance_instance.delete()

    return HttpResponse(u'删除成功')


@login_required()
@permission_verify()
def instance_edit(request, instance_id):
    project = Instance.objects.get(id=instance_id)
    if request.method == 'POST':
        form = InstanceForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('instance_index'))
    else:
        form = InstanceForm(instance=project)

    display_control = "none"
    results = {
        'instance_form': form,
        'instance_id': instance_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'cmdb/instance_base.html', results)


@login_required
@permission_verify()
def instance_detail(request, instance_id):
    instance = Instance.objects.get(id=instance_id)
    return render(request, 'cmdb/instance_detail.html', locals())
