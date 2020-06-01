#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from cmdb.models import HostService, ServiceSystem
from cmdb.forms import SystemForm, ProblemForm
from models import Problem
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from cmdb.api import get_object
from django.shortcuts import HttpResponse


@login_required()
@permission_verify()
def problem_add(request):
    if request.method == "POST":
        service_form = ProblemForm(request.POST)
        if service_form.is_valid():
            service_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        # 添加完成后，跳转到列表页面
        allproblems = Problem.objects.all()
        return render(request, "monitor/health-overview-problems.html", locals())
    else:
        display_control = "none"
        problem_form = ProblemForm()
        return render(request, "monitor/problem-base.html", locals())


def confirm_problem(problem_ids, status=2):
    if not isinstance(problem_ids, list):
        problem_ids = [problem_ids]

    if 2 == status:
        # 保留的方法
        # status=2时，让状态0/1互转
        for problem in Problem.objects.filter(id__in=problem_ids):
            problem.status = 0 if problem.status else 1
            problem.save()
    elif status in [0, 1]:
        Problem.objects.filter(id__in=problem_ids).update(status=status)


@login_required()
@permission_verify()
def clear_problems(request):
    problem_ids = request.GET.get('id', '')
    if request.method == 'POST':
        problem_batch = request.GET.get('arg', '')
        problem_id_all = str(request.POST.get('problem_id_all', ''))
        if problem_batch:
            problem_ids = problem_id_all.split(',')

    if problem_ids:
        if not isinstance(problem_ids, list):
            problem_ids = [problem_ids]

        Problem.objects.filter(id__in=problem_ids).update(status=1)     # 置为已确认
        for p in Problem.objects.filter(id__in=problem_ids):
            if p:
                target_problems = Problem.objects.filter(ip=p.ip, instance=p.instance, expr=p.expr,
                                                         source=p.source
                                                         ).exclude(id__in=problem_ids)
                target_problems.delete()
    return HttpResponse(u'执行成功')


@login_required()
@permission_verify()
def confirm_problems(request):
    status = int(request.GET.get('stat', ''))
    problem_id = request.GET.get('id', '')
    if problem_id:
        confirm_problem(problem_id, status=status)

    if request.method == 'POST':
        problem_batch = request.GET.get('arg', '')
        problem_id_all = str(request.POST.get('problem_id_all', ''))
        if problem_batch:
            problem_ids = problem_id_all.split(',')
            confirm_problem(problem_ids, status=status)

    return HttpResponse(u'执行成功')


@login_required()
@permission_verify()
def del_problems(request):
    problem_id = request.GET.get('id', '')
    if problem_id:
        Problem.objects.get(id=problem_id).delete()

    if request.method == 'POST':
        problem_batch = request.GET.get('arg', '')
        problem_id_all = str(request.POST.get('problem_id_all', ''))
        if problem_batch:
            problem_ids = problem_id_all.split(',')
            Problem.objects.filter(id__in=problem_ids).delete()

    return HttpResponse(u'执行成功')


# @login_required()
# @permission_verify()
# def del_problems(request):
#     group_id = request.GET.get('id', '')
#     if group_id:
#         Problem.objects.get(id=group_id).delete()
#
#     if request.method == 'POST':
#         group_items = request.POST.getlist('id', [])
#         if group_items:
#             for n in group_items:
#                 Problem.objects.filter(id=n).delete()
#
#     return HttpResponseRedirect(reverse('health_overview_problems'))


@login_required()
@permission_verify()
def problem_edit(request, problem_id):
    problem = Problem.objects.get(id=problem_id)
    if request.method == 'POST':
        form = ProblemForm(request.POST, instance=problem)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('health_overview_problems'))
    else:
        form = ProblemForm(instance=problem)
    display_control = "none"
    results = {
        'problem_form': form,
        'problem_id': problem_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'monitor/problem-base.html', results)


@login_required()
@permission_verify()
def problem_del(request, problem_id):
    Problem.objects.filter(id=problem_id).delete()
    return HttpResponseRedirect(reverse('health_overview_problems'))
