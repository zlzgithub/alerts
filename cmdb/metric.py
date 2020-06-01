#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from accounts.permission import permission_verify
from monitor.forms import MetricForm
from monitor.models import Metric

try:
    reload(sys)  # Python 2
    sys.setdefaultencoding('utf8')
except NameError:
    pass  # Python 3


@login_required()
@permission_verify()
def metrics(request):
    all_metrics = Metric.objects.all()
    context = {
        'allmetric': all_metrics
    }
    return render(request, 'cmdb/metric.html', context)


@login_required()
@permission_verify()
def metric_add(request):
    if request.method == "POST":
        metric_form = MetricForm(request.POST)
        if metric_form.is_valid():
            metric_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        # return render(request, "cmdb/metric_base.html", locals())
        # 添加完成后，跳转到列表页面
        # allmetric = Metric.objects.all()
        # return render(request, "cmdb/metrics.html", locals())
        # 不使用return render, 防止重复提交表单, 使用重定向url才一致
        return HttpResponseRedirect(reverse('metric_index'))
    else:
        display_control = "none"
        metric_form = MetricForm()
        return render(request, "cmdb/metric_base.html", locals())


@login_required()
@permission_verify()
def metric_del(request):
    metric_id = request.GET.get('id', '')
    if metric_id:
        Metric.objects.filter(id=metric_id).delete()

    if request.method == 'POST':
        metric_items = request.POST.getlist('g_check', [])
        if metric_items:
            for n in metric_items:
                Metric.objects.filter(id=n).delete()
    # allmetric = Metric.objects.all()
    # return render(request, "cmdb/metrics.html", locals())
    # 不使用return render, 防止重复提交表单, 使用重定向url才一致
    return HttpResponseRedirect(reverse('metric_index'))


@login_required()
@permission_verify()
def metric_edit(request, metric_id):
    project = Metric.objects.get(id=metric_id)
    if request.method == 'POST':
        form = MetricForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('metric_index'))
    else:
        form = MetricForm(instance=project)

    display_control = "none"
    results = {
        'metric_form': form,
        'metric_id': metric_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'cmdb/metric_base.html', results)


@login_required
@permission_verify()
def related_info(request, metric_id):
    grp = Metric.objects.get(id=metric_id)
    triggers = grp.triggerList.all()
    results = {
        'trigger_list': triggers,
    }
    return render(request, 'cmdb/metric_related_info.html', results)
