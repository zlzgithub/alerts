#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from accounts.permission import permission_verify
from cmdb.api import get_object
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, render
from cmdb.forms import RuleForm
from cmdb.models import Rule
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

try:
    reload(sys)  # Python 2
    sys.setdefaultencoding('utf8')
except NameError:
    pass  # Python 3


@login_required()
@permission_verify()
def rules(request):
    allrule = Rule.objects.all()
    context = {
        'allitem': allrule
    }
    return render(request, 'cmdb/rule.html', context)

#
# @login_required()
# @permission_verify()
# def rule2_add(request):
#     if request.method == "POST":
#         a_form = RuleForm(request.POST)
#         if a_form.is_valid():
#             a_form.save()
#             tips = u"增加成功！"
#             display_control = ""
#         else:
#             tips = u"增加失败！"
#             display_control = ""
#         return render(request, "cmdb/rule2_add.html", locals())
#     else:
#         display_control = "none"
#         a_form = RuleForm()
#         return render(request, "cmdb/rule2_add.html", locals())
#
#
# @login_required()
# @permission_verify()
# def rule2_del(request):
#     if 'GET' == request.method:
#         rule2_id = request.GET.get('id', '')
#         if rule2_id:
#             Rule.objects.filter(id=rule2_id).delete()
#         return HttpResponseRedirect(reverse('rule2_index'))
#
#     if 'POST' == request.method:
#         rule2_batch = request.GET.get('arg', '')
#         rule2_id_all = str(request.POST.get('rule2_id_all', ''))
#
#         if rule2_batch:
#             for rule2_id in rule2_id_all.split(','):
#                 rule2_rule = get_object(Item, id=rule2_id)
#                 rule2_rule.delete()
#
#     return HttpResponse(u'删除成功')
#
#
# @login_required
# @permission_verify()
# def rule2_edit000(request, ids):
#     status = 0
#     obj = get_object(Item, id=ids)
#     if request.method == 'POST':
#         af = ItemForm(request.POST, instance=obj)
#         if af.is_valid():
#             af.save()
#             status = 1
#         else:
#             status = 2
#     else:
#         af = ItemForm(instance=obj)
#
#     return render(request, 'cmdb/rule2_base.html', locals())
#
#
# @login_required()
# @permission_verify()
# def rule2_edit(request, rule2_id):
#     project = Rule.objects.get(id=rule2_id)
#     if request.method == 'POST':
#         form = ItemForm(request.POST, instance=project)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect(reverse('rule2_index'))
#     else:
#         form = ItemForm(instance=project)
#
#     display_control = "none"
#     results = {
#         'rule2_form': form,
#         'rule2_id': rule2_id,
#         'request': request,
#         'display_control': display_control,
#     }
#     return render(request, 'cmdb/rule2_base.html', results)
#
#
# @login_required
# @permission_verify()
# def rule2_detail(request, rule2_id):
#     rule = Rule.objects.get(id=rule2_id)
#     return render(request, 'cmdb/rule2_detail.html', locals())
#


@login_required()
@permission_verify()
def rule_add(request):
    if request.method == "POST":
        project = Rule.objects.create(editor=request.user.username)     # 设置editor
        rule_form = RuleForm(request.POST, instance=project)
        # rule_form = RuleForm(request.POST, initial={'editor': request.user.username})  # error ?
        if rule_form.is_valid():
            rule_form.save()
            tips = u"增加成功！"
            display_control = ""
        else:
            tips = u"增加失败！"
            display_control = ""
        # return render(request, "cmdb/rule_base.html", locals())
        # 添加完成后，跳转到列表页面
        # allrule = Rule.objects.all()
        # return render(request, "cmdb/rules.html", locals())
        # 不使用return render, 防止重复提交表单, 使用重定向url才一致
        return HttpResponseRedirect(reverse('rule_index'))
    else:
        display_control = "none"
        # rule_form = RuleForm(initial={'editor': request.user.username})
        rule_form = RuleForm()
        return render(request, "cmdb/rule_base.html", locals())


@login_required()
@permission_verify()
def rule_del000(request):
    rule_id = request.GET.get('id', '')
    if rule_id:
        Rule.objects.filter(id=rule_id).delete()

    if request.method == 'POST':
        rule_items = request.POST.getlist('g_check', [])
        if rule_items:
            for n in rule_items:
                Rule.objects.filter(id=n).delete()
    # allrule = Rule.objects.all()
    # return render(request, "cmdb/rules.html", locals())
    # 不使用return render, 防止重复提交表单, 使用重定向url才一致
    return HttpResponseRedirect(reverse('rule_index'))


@login_required()
@permission_verify()
def rule_del(request):
    if 'GET' == request.method:
        rule_id = request.GET.get('id', '')
        if rule_id:
            Rule.objects.filter(id=rule_id).delete()
        return HttpResponseRedirect(reverse('rule_index'))

    if 'POST' == request.method:
        rule_batch = request.GET.get('arg', '')
        rule_id_all = str(request.POST.get('rule_id_all', ''))

        if rule_batch:
            for rule_id in rule_id_all.split(','):
                rule_rule = get_object(Rule, id=rule_id)
                rule_rule.delete()

    return HttpResponse(u'删除成功')


@login_required()
@permission_verify()
def rule_edit(request, rule_id):
    project = Rule.objects.get(id=rule_id)
    if not project.editor:
        project.editor = request.user.username
    if request.method == 'POST':
        form = RuleForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('rule_index'))
    else:
        form = RuleForm(instance=project)

    display_control = "none"
    results = {
        'rule_form': form,
        'rule_id': rule_id,
        'request': request,
        'display_control': display_control,
    }
    return render(request, 'cmdb/rule_base.html', results)
