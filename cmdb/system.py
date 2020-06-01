#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from accounts.permission import permission_verify
from cmdb.forms import SystemForm
from cmdb.models import HostService, ServiceSystem


@login_required()
@permission_verify()
def system(request):
    allsystem = ServiceSystem.objects.all()
    context = {
        'allsystem': allsystem
    }
    return render(request, 'cmdb/systems.html', context)


@login_required()
@permission_verify()
def system_add(request):
    if request.method == "POST":
        system_form = SystemForm(request.POST)
        if system_form.is_valid():
            system_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        # 添加完成后，跳转到列表页面
        return HttpResponseRedirect(reverse('system'))
    else:
        display_control = "none"
        system_form = SystemForm()
        return render(request, "cmdb/system_base.html", locals())


@login_required()
@permission_verify()
def system_del(request):
    system_id = request.GET.get('id', '')
    if system_id:
        ServiceSystem.objects.filter(id=system_id).delete()

    if request.method == 'POST':
        system_items = request.POST.getlist('g_check', [])
        if system_items:
            for n in system_items:
                ServiceSystem.objects.filter(id=n).delete()

    return HttpResponseRedirect(reverse('system'))


@login_required()
@permission_verify()
def system_edit(request, system_id):
    project = ServiceSystem.objects.get(id=system_id)
    if request.method == 'POST':
        form = SystemForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('system'))
    else:
        form = SystemForm(instance=project)
    display_control = "none"
    results = {
        'system_form': form,
        'system_id': system_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'cmdb/system_base.html', results)


@login_required
@permission_verify()
def service_list(request, system_id):
    """
    点击系统名，弹窗显示所含服务列表页面
    :param request:
    :param system_id:
    :return:
    """
    grp = ServiceSystem.objects.get(id=system_id)
    services = grp.serviceList.all()
    svc_hosts = {}
    svc_hosts_list = []
    for svc in services:
        try:
            hosts = svc.serverList.all()
            svc_hosts[svc.name] = hosts
            svc_hosts_list.append({"svc_name": svc.name, "hosts": hosts})
        except HostService.DoesNotExist:
            pass

    results = {
        'item_list':  services,
        'svc_hosts_dict': svc_hosts,
        'svc_hosts_list': svc_hosts_list
    }
    return render(request, 'cmdb/system_service_list.html', results)
