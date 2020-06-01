#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.forms import RuleSetForm
from accounts.models import RuleSet
from accounts.permission import permission_verify


@login_required
@permission_verify()
def ruleset_add(request):
    if request.method == "POST":
        form = RuleSetForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('ruleset_list'))
    else:
        form = RuleSetForm()

    kwvars = {
        'form': form,
        'request': request,
    }

    return render(request, 'accounts/ruleset_add.html', kwvars)


@login_required
@permission_verify()
def ruleset_list(request):
    all_ruleset = RuleSet.objects.all()
    return render(request, 'accounts/ruleset_list.html', locals())


@login_required
@permission_verify()
def ruleset_edit(request, ids):
    iRule = RuleSet.objects.get(id=ids)
    if request.method == "POST":
        form = RuleSetForm(request.POST, instance=iRule)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('ruleset_list'))
    else:
        form = RuleSetForm(instance=iRule)

    kwvars = {
        'ids': ids,
        'form': form,
        'request': request,
    }

    return render(request, 'accounts/ruleset_edit.html', kwvars)


@login_required
@permission_verify()
def ruleset_del(request, ids):
    RuleSet.objects.filter(id=ids).delete()
    return HttpResponseRedirect(reverse('ruleset_list'))
