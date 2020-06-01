#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from cmdb.models import ServiceSystem, SystemGroup
from cmdb.forms import SystemGroupForm
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


@login_required()
@permission_verify()
def systemgroup(request):
    all_systemgroup = SystemGroup.objects.all()
    context = {
        'allsystemgroup': all_systemgroup
    }
    return render(request, 'cmdb/systemgroups.html', context)


@login_required()
@permission_verify()
def systemgroup_add(request):
    if request.method == "POST":
        systemgroup_form = SystemGroupForm(request.POST)
        if systemgroup_form.is_valid():
            systemgroup_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        return HttpResponseRedirect(reverse('systemgroup'))
    else:
        display_control = "none"
        systemgroup_form = SystemGroupForm()
        return render(request, "cmdb/systemgroup_base.html", locals())


@login_required()
@permission_verify()
def systemgroup_del(request):
    systemgroup_id = request.GET.get('id', '')
    if systemgroup_id:
        SystemGroup.objects.filter(id=systemgroup_id).delete()

    if request.method == 'POST':
        systemgroup_items = request.POST.getlist('g_check', [])
        if systemgroup_items:
            for n in systemgroup_items:
                SystemGroup.objects.filter(id=n).delete()

    return HttpResponseRedirect(reverse('systemgroup'))


@login_required()
@permission_verify()
def systemgroup_edit(request, systemgroup_id):
    systemgroup = SystemGroup.objects.get(id=systemgroup_id)
    if request.method == 'POST':
        form = SystemGroupForm(request.POST, instance=systemgroup)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('systemgroup'))
    else:
        form = SystemGroupForm(instance=systemgroup)
    display_control = "none"
    results = {
        'systemgroup_form': form,
        'systemgroup_id': systemgroup_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'cmdb/systemgroup_base.html', results)


@login_required
@permission_verify()
def system_list(request, systemgroup_id):
    """
    点击系统名，弹窗显示所含系统列表页面
    :param request:
    :param systemgroup_id:
    :return:
    """
    grp = SystemGroup.objects.get(id=systemgroup_id)
    systems = grp.systemList.all()
    sys_svcs = {}
    sys_svcs_list = []
    
    for sys in systems:
        try:
            svcs = sys.serviceList.all()
            sys_svcs[sys.name] = svcs
            sys_svcs_list.append({"sys_name": sys.name, "services": svcs})
        except ServiceSystem.DoesNotExist:
            pass

    results = {
        'item_list':  systems,
        'sys_svcs_dict': sys_svcs,
        'sys_svcs_list': sys_svcs_list
    }
    return render(request, 'cmdb/systemgroup_system_list.html', results)
