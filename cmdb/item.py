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
from cmdb.forms import ItemForm
from cmdb.models import Host
from monitor.health_api import get_plat_instances, get_plat_name
from monitor.models import Item
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
def get_items_data(request):
    print("get_items_data ...")
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

        all_ins = []
        is_all = False
        if aria_controls_id:
            all_ins = get_plat_instances(aria_controls_id=aria_controls_id)
        elif plat_id:
            all_ins = get_plat_instances(plat_id=plat_id)
        else:
            is_all = True

        if not is_all:
            kw.update({"instance__in": all_ins})
    else:
        host = Host.objects.get(id=host_id)
        host_ins = host.instanceList.all()
        kw.update({"instance__in": host_ins})

    # print("s_search:{} start:{} length:{} order:{}{}".format(
    #     s_search, start, length, order_type, order_col_name))
    if s_search:
        count = Item.objects.filter(**kw).filter(
            Q(instance__ip__icontains=s_search)
            | Q(instance__name__icontains=s_search)
            | Q(instance__name2__icontains=s_search)
            | Q(trigger__name__icontains=s_search)
            | Q(trigger__expr__icontains=s_search)).count()
        filtered_items = Item.objects.filter(**kw).filter(
            Q(instance__ip__icontains=s_search)
            | Q(instance__name__icontains=s_search)
            | Q(instance__name2__icontains=s_search)
            | Q(trigger__name__icontains=s_search)
            | Q(trigger__expr__icontains=s_search)
        ).order_by('{}{}'.format(order_type, order_col_name))[start:start + length]
    else:
        count = Item.objects.filter(**kw).count()        # all().count() ?
        filtered_items = Item.objects.filter(**kw).order_by(
            '{}{}'.format(order_type, order_col_name))[start:start + length]
        # filtered_items = Item.objects.all().order_by(
        #     '{}{}'.format(order_type, "instance__ip"))[start:start + length]
    if filtered_items:
        data = [{"id": p.id,
                 "instance__name": p.instance.name if p.instance else u"(unknown)",
                 "instance__name2": p.instance.name2 if p.instance else "--",
                 "instance__ip": p.instance.ip if p.instance else "--",
                 "trigger__name": p.trigger.name if p.trigger else "--",
                 "trigger__expr": p.trigger.expr if p.trigger else "--",
                 # "instance": {"name": p.instance.name,
                 #              "name2": p.instance.name2,
                 #              "ip": p.instance.ip} if
                 # p.instance else {"name": "(empty)",
                 #                  "name2": "",
                 #                  "ip": ""},
                 # "trigger": {"name": p.trigger.name, "expr": p.trigger.expr} if
                 # p.instance else {"name": "",
                 #                  "expr": ""}
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

    # print(json.dumps(dic))
    return JsonResponse(dic)


@login_required()
@permission_verify()
def items(request):
    url_get_items = '/cmdb/item/getitems/'
    plat_name = get_plat_name(request)
    return render(request, 'cmdb/item.html', locals())


@login_required()
@permission_verify()
def item_add(request):
    if request.method == "POST":
        a_form = ItemForm(request.POST)
        if a_form.is_valid():
            a_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        return render(request, "cmdb/item_add.html", locals())
    else:
        display_control = "none"
        a_form = ItemForm()
        return render(request, "cmdb/item_add.html", locals())


@login_required()
@permission_verify()
def item_del(request):
    if 'GET' == request.method:
        item_id = request.GET.get('id', '')
        if item_id:
            Item.objects.filter(id=item_id).delete()
        return HttpResponseRedirect(reverse('item_index'))

    if 'POST' == request.method:
        item_batch = request.GET.get('arg', '')
        item_id_all = str(request.POST.get('item_id_all', ''))

        if item_batch:
            for item_id in item_id_all.split(','):
                item_item = get_object(Item, id=item_id)
                item_item.delete()

    return HttpResponse(u'删除成功')


@login_required
@permission_verify()
def item_edit000(request, ids):
    status = 0
    obj = get_object(Item, id=ids)
    if request.method == 'POST':
        af = ItemForm(request.POST, instance=obj)
        if af.is_valid():
            af.save()
            status = 1
        else:
            status = 2
    else:
        af = ItemForm(instance=obj)

    return render(request, 'cmdb/item_base.html', locals())


@login_required()
@permission_verify()
def item_edit(request, item_id):
    project = Item.objects.get(id=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('item_index'))
    else:
        form = ItemForm(instance=project)

    display_control = "none"
    results = {
        'item_form': form,
        'item_id': item_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'cmdb/item_base.html', results)


@login_required
@permission_verify()
def item_detail(request, item_id):
    item = Item.objects.get(id=item_id)
    return render(request, 'cmdb/item_detail.html', locals())
