#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse, render
from accounts.permission import permission_verify
from cmdb.api import get_object
from cmdb.forms import TriggerForm
from cmdb.models import Host
from monitor.health_api import get_plat_instances, get_plat_name
from monitor.models import Trigger, Item
from django.db.models import Count, Q
from django.http import JsonResponse


try:
    reload(sys)  # Python 2
    sys.setdefaultencoding('utf8')
except NameError:
    pass  # Python 3


@login_required()
@permission_verify()
def get_triggers_data(request):
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
        # all_ids = [ins.id for ins in all_ins]
        kw.update({"trigger_itemList__instance__in": all_ins})        # todo
        if s_search:
            count = Trigger.objects.filter(**kw).filter(
                Q(name__icontains=s_search) |
                Q(expr__icontains=s_search)
            ).distinct().count()
            filtered_items = Trigger.objects.filter(**kw).filter(
                Q(name__icontains=s_search) |
                Q(expr__icontains=s_search)
            ).distinct().order_by('{}{}'.format(order_type, order_col_name))[start:start + length]
        else:
            count = Trigger.objects.filter(**kw).distinct().count()
            filtered_items = Trigger.objects.filter(**kw).distinct().order_by(
                '{}{}'.format(order_type, order_col_name))[start:start + length]
    else:
        if s_search:
            count = Trigger.objects.filter(
                Q(name__icontains=s_search) |
                Q(expr__icontains=s_search)).count()
            filtered_items = Trigger.objects.filter(
                Q(name__icontains=s_search) |
                Q(expr__icontains=s_search)
            ).order_by('{}{}'.format(order_type, order_col_name))[start:start + length]
        else:
            count = Trigger.objects.count()
            filtered_items = Trigger.objects.order_by(
                '{}{}'.format(order_type, order_col_name))[start:start + length]

    if filtered_items:
        data = [{"id": p.id, "name": p.name, "expr": p.expr} for p in filtered_items]
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
def triggers(request):
    url_get_items = '/cmdb/trigger/gettriggers/'
    plat_name = get_plat_name(request)
    return render(request, 'cmdb/trigger.html', locals())


@login_required()
@permission_verify()
def trigger_add(request):
    if request.method == "POST":
        a_form = TriggerForm(request.POST)
        if a_form.is_valid():
            a_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        return render(request, "cmdb/trigger_add.html", locals())
    else:
        display_control = "none"
        a_form = TriggerForm()
        return render(request, "cmdb/trigger_add.html", locals())


@login_required()
@permission_verify()
def trigger_del(request):
    if 'GET' == request.method:
        trigger_id = request.GET.get('id', '')
        if trigger_id:
            Trigger.objects.filter(id=trigger_id).delete()
        return HttpResponseRedirect(reverse('trigger_index'))

    if 'POST' == request.method:
        trigger_batch = request.GET.get('arg', '')
        trigger_id_all = str(request.POST.get('trigger_id_all', ''))

        if trigger_batch:
            for trigger_id in trigger_id_all.split(','):
                trigger_trigger = get_object(Trigger, id=trigger_id)
                trigger_trigger.delete()

    return HttpResponse(u'删除成功')


@login_required()
@permission_verify()
def trigger_edit(request, trigger_id):
    project = Trigger.objects.get(id=trigger_id)
    if request.method == 'POST':
        form = TriggerForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('trigger_index'))
    else:
        form = TriggerForm(instance=project)

    display_control = "none"
    results = {
        'trigger_form': form,
        'trigger_id': trigger_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'cmdb/trigger_base.html', results)


@login_required
@permission_verify()
def trigger_detail(request, trigger_id):
    trigger = Trigger.objects.get(id=trigger_id)
    return render(request, 'cmdb/trigger_detail.html', locals())
