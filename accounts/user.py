#! /usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os

from django.shortcuts import render, HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from accounts.forms import LoginUserForm, EditUserForm, ChangePasswordForm, ChangeLdapPasswordForm
from django.contrib.auth import get_user_model
from accounts.forms import AddUserForm
from django.core.urlresolvers import reverse
from accounts.models import UserInfo, RoleList, RuleSet
from accounts.permission import permission_verify
from accounts.gldap import change_ldap_passwd
from cmdb.api import str2gb2utf8


def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    if request.method == 'GET' and request.GET.has_key('next'):
        next_page = request.GET['next']
    else:
        next_page = '/'
    if next_page == "/accounts/logout/":
        next_page = '/'
    if request.method == "POST":
        form = LoginUserForm(request, data=request.POST)
        if form.is_valid():
            # auth.login(request, form.get_user())
            user = form.get_user()
            auth.login(request, user)
            if not user.role and 'admin' != user.username:
                try:
                    def_role = RoleList.objects.get(name="normal")
                    if def_role:
                        user.role = def_role
                        user.save()
                except RoleList.DoesNotExist:
                    print("Role [normal] does not exist")
                    pass
            return HttpResponseRedirect(request.POST['next'])
    else:
        form = LoginUserForm(request)
    kwargs = {
        'request': request,
        'form':  form,
        'next': next_page,
    }
    return render(request, 'accounts/login.html', kwargs)


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required()
@permission_verify()
def user_list(request):
    all_user = get_user_model().objects.all()
    request_user = UserInfo.objects.get(username=request.user.username)
    if str(request_user.role) not in ['ops'] and request_user.username != 'admin':
        all_user = get_user_model().objects.filter(username=request_user.username)

    if str(request_user.role) in ['ops']:
        all_user = all_user.exclude(username='admin')

    kwargs = {
        'all_user':  all_user,
    }
    return render(request, 'accounts/user_list.html', kwargs)


@login_required
@permission_verify()
def user_add(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            form.save()
            return HttpResponseRedirect(reverse('user_list'))
    else:
        form = AddUserForm()
    kwargs = {
        'form': form,
        'request': request,
    }
    return render(request, 'accounts/user_add.html', kwargs)


@login_required
@permission_verify()
def user_del(request, ids):
    if ids:
        t_user = UserInfo.objects.get(id=ids)
        request_user = UserInfo.objects.get(username=request.user.username)
        if str(request_user.role) not in ['ops'] and request_user.username != 'admin':
            return HttpResponse(u"<font color=red>不能删除此用户！</font>")
        if t_user.username not in ['admin', request.user.username]:
            get_user_model().objects.filter(id=ids).delete()
    return HttpResponseRedirect(reverse('user_list'))


@login_required
@permission_verify()
def user_edit(request, ids):
    user = get_user_model().objects.get(id=ids)
    ldap_name = user.ldap_name
    request_user = UserInfo.objects.get(username=request.user.username)
    if str(request_user.role) not in ['ops'] and request_user.username != 'admin':
        if user.username != request_user.username:
            return HttpResponse(u"<font color=red>不能编辑此用户！</font>")

    if str(request_user.role) in ['ops'] and user.username == 'admin':
        return HttpResponse(u"<font color=red>不能编辑admin！</font>")

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            status = 1
        else:
            status = 2
    else:
        form = EditUserForm(instance=user)
    return render(request, 'accounts/user_edit.html', locals())


@login_required
@permission_verify()
def reset_password(request, ids):
    user = get_user_model().objects.get(id=ids)
    newpassword = get_user_model().objects.make_random_password(length=10, allowed_chars='abcdefghjklmnpqrstuvwxyABCDEFGHJKLMNPQRSTUVWXY3456789')
    print('====>ResetPassword:{}-->{}'.format(user.username, newpassword))
    user.set_password(newpassword)
    user.save()
    kwargs = {
        'object': user,
        'newpassword': newpassword,
        'request': request,
    }
    return render(request, 'accounts/reset_password.html', kwargs)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_list'))
    else:
        form = ChangePasswordForm(user=request.user)
    kwargs = {
        'form': form,
        'request': request,
    }
    return render(request, 'accounts/change_password.html', kwargs)


@login_required
def change_ldap(request):
    if request.method == 'POST':
        form = ChangeLdapPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            newpwd = form.clean_new_password2()
            change_ldap_passwd(request.user, newpwd)
            return HttpResponseRedirect(reverse('user_list'))
    else:
        form = ChangeLdapPasswordForm(user=request.user)
    kwargs = {
        'form': form,
        'request': request,
    }
    return render(request, 'accounts/change_ldap_password.html', kwargs)


@login_required()
@permission_verify()
def user_import(request):
    if request.method == "POST":
        uf = request.FILES.get('user_import')
        with open("/var/opt/alerts/data/user.csv", "wb+") as f:
            for chunk in uf.chunks(chunk_size=1024):
                f.write(chunk)
        try:
            filename = "/var/opt/alerts/data/user.csv"
            with open(filename, "rb") as f:
                title = next(csv.reader(f))
                for data in csv.reader(f):
                    data0 = str2gb2utf8(data[0])
                    if "username" == data0:
                        continue
                    try:
                        user = UserInfo.objects.get(username=data0)
                    except Exception as msg:
                        user = UserInfo()
                        user.username = data0

                    user.email = data[1]
                    user.is_active = data[2]
                    user.is_superuser = data[3]
                    user.nickname = str2gb2utf8(data[4])
                    user.ldap_name = data[5]
                    if data[6]:
                        try:
                            role = str2gb2utf8(data[6])
                            item = RoleList.objects.get(name=role)
                            user.role_id = item.id
                        except Exception as e:
                            print(e)
                            print("role info import error")
                    user.is_alert_enabled = data[7]
                    if data[8]:
                        try:
                            ruleset = str2gb2utf8(data[8])
                            item = RuleSet.objects.get(name=ruleset)
                            user.ruleset_id = item.id
                        except Exception as e:
                            print("ruleset info import error!")
                    user.wid = data[9]
                    user.set_password("password")       # 初始默认密码 "password"
                    user.save()
            os.remove(filename)
            status = 1
        except Exception as e:
            print("import user csv file error!")
            status = 2

    return render(request, 'accounts/import.html', locals())
