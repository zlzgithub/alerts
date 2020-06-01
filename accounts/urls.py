#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from accounts import user, role, rule, permission, gldap

urlpatterns = [
    # url(r'^$', user.user_list, name='accounts'),
    url(r'^login/$', user.login, name='login'),
    url(r'^logout/$', user.logout, name='logout'),

    url(r'^userlist/$', user.user_list, name='user_list'),
    url(r'^useradd/$', user.user_add, name='user_add'),
    url(r'^userimport/$', user.user_import, name='user_import'),
    url(r'^userdelete/(?P<ids>\d+)/$', user.user_del, name='user_del'),
    url(r'^useredit/(?P<ids>\d+)/$', user.user_edit, name='user_edit'),
    url(r'^resetpassword/(?P<ids>\d+)/$', user.reset_password, name='reset_password'),
    url(r'^changepassword/$', user.change_password, name='change_password'),
    url(r'^changeldappassword/$', user.change_ldap, name='change_ldap_password'),

    url(r'^roleadd/$', role.role_add, name='role_add'),
    url(r'^rolelist/$', role.role_list, name='role_list'),
    url(r'^roleedit/(?P<ids>\d+)/$', role.role_edit, name='role_edit'),
    url(r'^roledelete/(?P<ids>\d+)/$', role.role_del, name='role_del'),

    url(r'^rulesetlist/$', rule.ruleset_list, name='ruleset_list'),
    url(r'^rulesetadd/$', rule.ruleset_add, name='ruleset_add'),
    url(r'^rulesetedit/(?P<ids>\d+)/$', rule.ruleset_edit, name='ruleset_edit'),
    url(r'^rulesetdelete/(?P<ids>\d+)/$', rule.ruleset_del, name='ruleset_del'),

    url(r'^permdeny/$', permission.permission_deny, name='permission_deny'),
    url(r'^permadd/$', permission.permission_add, name='permission_add'),
    url(r'^permlist/$', permission.permission_list, name='permission_list'),
    url(r'^permedit/(?P<ids>\d+)/$', permission.permission_edit, name='permission_edit'),
    url(r'^permdel/(?P<ids>\d+)/$', permission.permission_del, name='permission_del'),
    url(r'^permission/user_permission/$', permission.get_user_permission,
        name='get_user_permission'),
]
