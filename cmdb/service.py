#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from cmdb.models import HostService, Host
from cmdb.forms import ServiceForm
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import HttpResponse


@login_required()
@permission_verify()
def service(request):
    allservice = HostService.objects.all()
    context = {
        'allservice': allservice,
    }
    return render(request, 'cmdb/service.html', context)


@login_required()
@permission_verify()
def service_add(request):
    if request.method == "POST":
        service_form = ServiceForm(request.POST)
        if service_form.is_valid():
            service_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        # 添加完成后，跳转到列表页面
        # 不使用return render, 防止重复提交表单, 使用重定向url才一致
        return HttpResponseRedirect(reverse('service'))
    else:
        display_control = "none"
        service_form = ServiceForm()
        return render(request, "cmdb/service_base.html", locals())


@login_required()
@permission_verify()
def service_del(request):
    service_id = request.GET.get('id', '')
    if service_id:
        HostService.objects.filter(id=service_id).delete()

    if request.method == 'POST':
        service_items = request.POST.getlist('g_check', [])
        if service_items:
            for n in service_items:
                HostService.objects.filter(id=n).delete()

    return HttpResponseRedirect(reverse('service'))


# todo 以下为测试代码
def service_edit5(request, service_id):
    add_ids = [50, 51, 52]
    service = HostService.objects.get(id=service_id)
    new_hosts = Host.objects.filter(id__in=add_ids)
    service.serverList.add(*new_hosts)  # 注意星号*
    return HttpResponse(u'添加成功？')


def service_edit4(request, service_id):
    service = HostService.objects.get(id=service_id)
    new_hosts = Host.objects.get(id=46)
    service.serverList.add(new_hosts)
    return HttpResponse(u'添加成功？')


def service_edit3(request, service_id):
    add_ids = 40
    service = HostService.objects.get(id=service_id)
    service.serverList.add(add_ids)
    return HttpResponse(u'添加成功？')


def service_edit2(request, service_id):
    server_ids = ['12', '15', '23', '25']
    data = {
        'serverList': server_ids,
        # 'serverList_helper2': server_ids,
        'name': 'Redis',
        'desc': 'Redis ......'
    }
    try:
        project = HostService.objects.get(id=service_id)
        form = ServiceForm(data, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponse(u'执行成功')
    except HostService.DoesNotExist:
        form = ServiceForm(data)
        if form.is_valid():
            form.save()
            return HttpResponse(u'创建成功')

    return HttpResponse(u'执行失败')


@login_required()
@permission_verify()
def service_edit(request, service_id):
    project = HostService.objects.get(id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('service'))
    else:
        form = ServiceForm(instance=project)
    display_control = "none"
    results = {
        'service_form': form,
        'service_id': service_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'cmdb/service_base.html', results)


@login_required
@permission_verify()
def server_list(request, service_id):
    """
    点击服务名，显示弹窗列表页面
    :param request:
    :param service_id:
    :return:
    """
    grp = HostService.objects.get(id=service_id)
    servers = grp.serverList.all()
    results = {
        'server_list': servers,
    }
    return render(request, 'cmdb/service_server_list.html', results)
