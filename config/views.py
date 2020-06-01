#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import re
import requests
from django.shortcuts import render, HttpResponse

try:
    import configparser as cp
except Exception as msg:
    print(msg)
    import ConfigParser as cp
import os
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify
from django.contrib.auth import get_user_model
from lib.log import dic


@login_required()
@permission_verify()
def index(request):
    temp_name = "config/config-header.html"
    display_control = "none"
    dirs = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config = cp.RawConfigParser()
    all_level = dic
    all_filter = ("OpenLDAP", "WindowsAD")
    ldap_choice = ("True", "False")
    with open(dirs + '/alerts.conf', 'r') as cfgfile:
        config.readfp(cfgfile)
        engine = config.get('db', 'engine')
        host = config.get('db', 'host')
        port = config.get('db', 'port')
        user = config.get('db', 'user')
        password = config.get('db', 'password')
        database = config.get('db', 'database')
        token = config.get('token', 'token')
        secret_key = config.get('secret_key', 'secret_key')
        log_path = config.get('log', 'log_path')
        log_level = config.get('log', 'log_level')
        mongodb_ip = config.get('mongodb', 'mongodb_ip')
        mongodb_port = config.get('mongodb', 'mongodb_port')
        mongodb_user = config.get('mongodb', 'mongodb_user')
        mongodb_pwd = config.get('mongodb', 'mongodb_pwd')
        mongodb_collection = config.get('mongodb', 'collection')
        redis_host = config.get('redis', 'redis_host')
        redis_port = config.get('redis', 'redis_port')
        redis_password = config.get('redis', 'redis_password')
        redis_db = config.get('redis', 'redis_db')
        ldap_enable = config.get('ldap', 'ldap_enable')
        ldap_server = config.get('ldap', 'ldap_server')
        ldap_port = config.get('ldap', 'ldap_port')
        base_dn = config.get('ldap', 'base_dn')
        ldap_manager = config.get('ldap', 'ldap_manager')
        ldap_password = config.get('ldap', 'ldap_password')
        ldap_filter = config.get('ldap', 'ldap_filter')
        require_group = config.get('ldap', 'require_group')
        nickname = config.get('ldap', 'nickname')
        is_active = config.get('ldap', 'is_active')
        is_superuser = config.get('ldap', 'is_superuser')
        wx_corpid = config.get('wx', 'wx_corpid')
        wx_secret = config.get('wx', 'wx_secret')
        wx_agentid = config.get('wx', 'wx_agentid')
    return render(request, 'config/index.html', locals())


@login_required()
@permission_verify()
def config_save(request):
    temp_name = "config/config-header.html"
    if request.method == 'POST':
        # db
        engine = request.POST.get('engine')
        host = request.POST.get('host')
        port = request.POST.get('port')
        user = request.POST.get('user')
        password = request.POST.get('password')
        database = request.POST.get('database')
        # cmdb_api_token
        token = request.POST.get('token')
        secret_key = request.POST.get('secret_key')
        # log
        log_path = request.POST.get('log_path')
        log_level = request.POST.get('log_level')
        # mongodb
        mongodb_ip = request.POST.get('mongodb_ip')
        mongodb_port = request.POST.get('mongodb_port')
        mongodb_user = request.POST.get('mongodb_user')
        mongodb_pwd = request.POST.get('mongodb_pwd')
        mongodb_collection = request.POST.get('mongodb_collection')
        # redis
        redis_host = request.POST.get('redis_host')
        redis_port = request.POST.get('redis_port')
        redis_password = request.POST.get('redis_password')
        redis_db = request.POST.get('redis_db')
        # ldap
        ldap_enable = request.POST.get('ldap_enable')
        ldap_server = request.POST.get('ldap_server')
        ldap_port = request.POST.get('ldap_port')
        base_dn = request.POST.get('base_dn')
        ldap_manager = request.POST.get('ldap_manager')
        ldap_password = request.POST.get('ldap_password')
        ldap_filter = request.POST.get('ldap_filter')
        require_group = request.POST.get('require_group')
        nickname = request.POST.get('nickname')
        is_active = request.POST.get('is_active')
        is_superuser = request.POST.get('is_superuser')
        # wx
        wx_corpid = request.POST.get('wx_corpid')
        wx_secret = request.POST.get('wx_secret')
        wx_agentid = request.POST.get('wx_agentid')

        config = cp.RawConfigParser()
        dirs = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config.add_section('db')
        config.set('db', 'engine', engine)
        config.set('db', 'host', host)
        config.set('db', 'port', port)
        config.set('db', 'user', user)
        config.set('db', 'password', password)
        config.set('db', 'database', database)
        config.add_section('token')
        config.set('token', 'token', token)
        config.add_section('secret_key')
        config.set('secret_key', 'secret_key', secret_key)
        config.add_section('log')
        config.set('log', 'log_path', log_path)
        config.set('log', 'log_level', log_level)
        config.add_section('mongodb')
        config.set('mongodb', 'mongodb_ip', mongodb_ip)
        config.set('mongodb', 'mongodb_port', mongodb_port)
        config.set('mongodb', 'mongodb_user', mongodb_user)
        config.set('mongodb', 'mongodb_pwd', mongodb_pwd)
        config.set('mongodb', 'collection', mongodb_collection)
        config.add_section('redis')
        config.set('redis', 'redis_host', redis_host)
        config.set('redis', 'redis_port', redis_port)
        config.set('redis', 'redis_password', redis_password)
        config.set('redis', 'redis_db', redis_db)
        config.add_section('ldap')
        config.set('ldap', 'ldap_enable', ldap_enable)
        config.set('ldap', 'ldap_server', ldap_server)
        config.set('ldap', 'ldap_port', ldap_port)
        config.set('ldap', 'base_dn', base_dn)
        config.set('ldap', 'ldap_manager', ldap_manager)
        config.set('ldap', 'ldap_password', ldap_password)
        config.set('ldap', 'ldap_filter', ldap_filter)
        config.set('ldap', 'require_group', require_group)
        config.set('ldap', 'nickname', nickname)
        config.set('ldap', 'is_active', is_active)
        config.set('ldap', 'is_superuser', is_superuser)
        config.add_section('wx')
        config.set('wx', 'wx_corpid', wx_corpid)
        config.set('wx', 'wx_secret', wx_secret)
        config.set('wx', 'wx_agentid', wx_agentid)

        tips = u"保存成功！"
        display_control = ""
        with open(dirs + '/alerts.conf', 'wb') as cfgfile:
            config.write(cfgfile)
        with open(dirs + '/alerts.conf', 'r') as cfgfile:
            config.readfp(cfgfile)
            engine = config.get('db', 'engine')
            host = config.get('db', 'host')
            port = config.get('db', 'port')
            user = config.get('db', 'user')
            password = config.get('db', 'password')
            database = config.get('db', 'database')
            token = config.get('token', 'token')
            secret_key = config.get('secret_key', 'secret_key')
            log_path = config.get('log', 'log_path')
            mongodb_ip = config.get('mongodb', 'mongodb_ip')
            mongodb_port = config.get('mongodb', 'mongodb_port')
            mongodb_user = config.get('mongodb', 'mongodb_user')
            mongodb_pwd = config.get('mongodb', 'mongodb_pwd')
            mongodb_collection = config.get('mongodb', 'collection')
            redis_host = config.get('redis', 'redis_host')
            redis_port = config.get('redis', 'redis_port')
            redis_password = config.get('redis', 'redis_password')
            redis_db = config.get('redis', 'redis_db')
            ldap_enable = config.get('ldap', 'ldap_enable')
            ldap_server = config.get('ldap', 'ldap_server')
            ldap_port = config.get('ldap', 'ldap_port')
            base_dn = config.get('ldap', 'base_dn')
            ldap_manager = config.get('ldap', 'ldap_manager')
            ldap_password = config.get('ldap', 'ldap_password')
            ldap_filter = config.get('ldap', 'ldap_filter')
            require_group = config.get('ldap', 'require_group')
            nickname = config.get('ldap', 'nickname')
            is_active = config.get('ldap', 'is_active')
            is_superuser = config.get('ldap', 'is_superuser')
            wx_corpid = config.get('wx', 'wx_corpid')
            wx_secret = config.get('wx', 'wx_secret')
            wx_agentid = config.get('wx', 'wx_agentid')
    else:
        display_control = "none"
    return render(request, 'config/index.html', locals())


def get_dir(args):
    config = cp.RawConfigParser()
    dirs = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(dirs + '/alerts.conf', 'r') as cfgfile:
        config.readfp(cfgfile)
        token = config.get('token', 'token')
        secret_key = config.get('secret_key', 'secret_key')
        log_path = config.get('log', 'log_path')
        log_level = config.get('log', 'log_level')
        mongodb_ip = config.get('mongodb', 'mongodb_ip')
        mongodb_port = config.get('mongodb', 'mongodb_port')
        mongodb_user = config.get('mongodb', 'mongodb_user')
        mongodb_pwd = config.get('mongodb', 'mongodb_pwd')
        mongodb_collection = config.get('mongodb', 'collection')
        redis_host = config.get('redis', 'redis_host')
        redis_port = config.get('redis', 'redis_port')
        redis_password = config.get('redis', 'redis_password')
        redis_db = config.get('redis', 'redis_db')
        ldap_enable = config.get('ldap', 'ldap_enable')
        ldap_server = config.get('ldap', 'ldap_server')
        ldap_port = config.get('ldap', 'ldap_port')
        base_dn = config.get('ldap', 'base_dn')
        ldap_manager = config.get('ldap', 'ldap_manager')
        ldap_password = config.get('ldap', 'ldap_password')
        ldap_filter = config.get('ldap', 'ldap_filter')
        require_group = config.get('ldap', 'require_group')
        nickname = config.get('ldap', 'nickname')
        is_active = config.get('ldap', 'is_active')
        is_superuser = config.get('ldap', 'is_superuser')
        wx_corpid = config.get('wx', 'wx_corpid')
        wx_secret = config.get('wx', 'wx_secret')
        wx_agentid = config.get('wx', 'wx_agentid')

    # 根据传入参数返回变量以获取配置，返回变量名与参数名相同
    if args:
        return vars()[args]
    else:
        return HttpResponse(status=403)


@login_required()
@permission_verify()
def get_token(request):
    if request.method == 'POST':
        new_token = get_user_model().objects.make_random_password(length=12,
                                                                  allowed_chars='abcdefghjklmnpqrstuvwxyABCDEFGHJKLMNPQRSTUVWXY3456789')
        return HttpResponse(new_token)
    else:
        return True
