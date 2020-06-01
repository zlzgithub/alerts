#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json
import time

from django.db.models import Max
from django.db.models.query import QuerySet
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from pymongo import MongoClient
from accounts.models import UserInfo
from cmdb.models import Host, HostService, Instance, Rule
from config.views import get_dir
from lib.common import token_verify
from monitor.health_api import get_host_group_info
from monitor.models import Problem, Trigger, Metric, Item, Notification
from monitor.tasks import alert_task
from monitor.utils.log import logger
from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify


class GetSysData(object):
    db = get_dir("mongodb_collection")

    def __init__(self, hostname, monitor_item, timing, no=0):
        self.hostname = hostname
        self.monitor_item = monitor_item
        self.timing = timing
        self.no = no

    @classmethod
    def connect_db(cls):
        mongodb_ip = get_dir("mongodb_ip")
        mongodb_port = get_dir("mongodb_port")
        mongodb_user = get_dir("mongodb_user")
        mongodb_pwd = get_dir("mongodb_pwd")
        if mongodb_user:
            uri = 'mongodb://' + mongodb_user + ':' + mongodb_pwd + '@' + mongodb_ip + ':' + mongodb_port + '/' + cls.db
            client = MongoClient(uri)
        else:
            client = MongoClient(mongodb_ip, int(mongodb_port))
        return client

    def get_data(self):
        client = self.connect_db()
        db = client[self.db]
        collection = db[self.hostname]
        now_time = int(time.time())
        find_time = now_time - self.timing
        cursor = collection.find({'timestamp': {'$gte': find_time}},
                                 {self.monitor_item: 1, "timestamp": 1}).limit(self.no)
        return cursor


class GetSyslinkData(object):
    db = 'syslink_info'
    coll = 'edge_path'

    def __init__(self, timing, no=0, sort=-1):
        self.timing = timing
        self.no = no
        self.sort = sort

    @classmethod
    def connect_db(cls):
        mongodb_ip = get_dir("mongodb_ip")
        mongodb_port = get_dir("mongodb_port")
        mongodb_user = get_dir("mongodb_user")
        mongodb_pwd = get_dir("mongodb_pwd")
        if mongodb_user:
            uri = 'mongodb://' + mongodb_user + ':' + mongodb_pwd + '@' + mongodb_ip + ':' + mongodb_port + '/' + cls.db
            client = MongoClient(uri)
        else:
            client = MongoClient(mongodb_ip, int(mongodb_port))
        return client

    def get_data(self):
        client = self.connect_db()
        db = client[self.db]
        collection = db[self.coll]
        now_time = int(time.time())
        find_time = now_time - self.timing
        # cursor = collection.find(
        #     {'timestamp': {'$gte': find_time}},
        #     {"timestamp": 1, "from": 1, "to": 1, "status": 1, "title": 1, "result": 1}
        # ).limit(self.no)
        cursor = collection.find(
            {'timestamp': {'$gte': find_time}}).sort("_id", self.sort).limit(self.no)
        return cursor


@csrf_exempt
@token_verify()
def received_sys_info(request):
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        hostname = received_json_data["hostname"]
        received_json_data['timestamp'] = int(time.time())
        client = GetSysData.connect_db()
        db = client[GetSysData.db]
        collection = db[hostname]
        collection.insert_one(received_json_data)
        return HttpResponse("Post the system Monitor Data successfully!")
    else:
        return HttpResponse("Your push have errors, Please Check your data!")


@csrf_exempt
@token_verify()
def received_syslink_info(request):
    logger.info("[received_syslink_info] ...")
    if request.method == 'POST':
        received_json_data = json.loads(request.body)
        received_json_data['timestamp'] = int(time.time())
        client = GetSyslinkData.connect_db()
        db = client[GetSyslinkData.db]
        collection = db[GetSyslinkData.coll]
        del received_json_data["token"]
        collection.insert_one(received_json_data)
        return HttpResponse("Post the syslink Data successfully!")
    else:
        return HttpResponse("Your push have errors, Please Check your data!")


@csrf_exempt
@token_verify()
def received_syslink_data(request):
    logger.info("[received_syslink_data] ...")
    if request.method == 'POST':
        try:
            received_json_data = json.loads(request.body)
            if "data" in received_json_data and isinstance(received_json_data['data'], list):
                ts = int(time.time())
                client = GetSyslinkData.connect_db()
                db = client[GetSyslinkData.db]
                collection = db[GetSyslinkData.coll]
                for d in received_json_data['data']:
                    print("data d:")
                    print(str(d))
                    d['timestamp'] = ts
                    collection.insert_one(d)
            else:
                print("data:")
                print(str(received_json_data))
                received_json_data['timestamp'] = int(time.time())
                client = GetSyslinkData.connect_db()
                db = client[GetSyslinkData.db]
                collection = db[GetSyslinkData.coll]
                del received_json_data["token"]
                collection.insert_one(received_json_data)
            return HttpResponse("Post the syslink Data successfully!")
        except Exception as e:
            print(str(e))

    return HttpResponse("Your push have errors, Please Check your data!")


# @csrf_exempt
# @token_verify()
@login_required()
@permission_verify()
def refresh_item_id__isnull_problems(request):
    problems = Problem.objects.filter(item_id__isnull=True)
    res = update_from_new_problem(problems)
    s_res = json.dumps(res, indent=4)
    return HttpResponse('<pre>{}</pre>'.format(s_res))


def default_bind_trigger_to_metric(trigger):
    """
    默认分配metric方法
    :return:
    """
    matched_met = None
    try:
        if 'cpu' in trigger.expr.lower():
            matched_met = Metric.objects.filter(name__contains='CPU').first()
        elif 'memory' in trigger.expr.lower():
            matched_met = Metric.objects.filter(name__contains=u'内存').first()
        elif 'fs.size' in trigger.expr.lower():
            matched_met = Metric.objects.filter(name__contains=u'磁盘').first()
        elif 'disk' in trigger.expr.lower():
            matched_met = Metric.objects.filter(name__contains=u'磁盘').first()
        elif 'network' in trigger.expr.lower():
            matched_met = Metric.objects.filter(name__contains=u'网络').first()
        elif 'ping' in trigger.expr.lower():
            matched_met = Metric.objects.filter(name__contains=u'网络').first()
        elif 'probe_success' in trigger.expr.lower():
            matched_met = Metric.objects.filter(name__contains=u'网络').first()
        elif 'service' in trigger.expr.lower():
            matched_met = Metric.objects.filter(name__contains=u'服务').first()
        else:
            print("unmatched trigger: " + str(trigger.expr.lower()))
    except:
        pass

    return matched_met


def update_from_new_problem(problems=None):
    """
    更新各表的方法，待改进
    :param problems:
    :return:
    """
    new_problems = problems
    if not isinstance(problems, QuerySet) and not isinstance(problems, list):
        new_problems = [problems]
        # return HttpResponse("Parameter is not <QuerySet> ?")

    res_dict = {
        "trigger succeed": 0,
        "instance succeed": 0,
        "item succeed": 0,
        "item new": 0,
        "trigger failed": 0,
        "instance failed": 0,
        "item failed": 0,
        "problems": 0,
        "not expr": 0,
        "host update succeed": 0,
        "host update failed": 0,
        "attach instance succeed": 0,
        "attach instance failed": 0,
        "problem update succeed": 0,
        "problem update failed": 0
    }

    for p in new_problems:
        res_dict["problems"] += 1
        if not p.expr:
            res_dict["not expr"] += 1
            continue

        trigger = None
        try:
            # trigger = Trigger.objects.get(name=p.expr, expr=p.expr)
            trigger = Trigger.objects.filter(name=p.expr, expr=p.expr).first()
        except Trigger.DoesNotExist:
            try:
                trigger = Trigger.objects.create(name=p.expr, expr=p.expr)
                res_dict["trigger succeed"] += 1
            except:
                res_dict["trigger failed"] += 1

        try:
            trigger_metrics = trigger.metric_set.all()
            if not trigger_metrics:
                print("if not trigger_metrics:")
                all_met = Metric.objects.all()
                n_chk_match = 0
                matched_met = None
                for met in [m for m in all_met if u'其它' not in m.name]:
                    met_kws = met.kw_include.replace(' ', '').replace('|', ',').replace('，', ',')
                    # 正筛
                    if met_kws.replace(',', ''):
                        for kw in met_kws.split(','):
                            if kw and kw.lower() in trigger.expr.lower():
                                n_chk_match = 1
                                matched_met = met
                                print("matched: " + met.name)
                                print("matched: " + kw.lower() + " -> "
                                      + trigger.expr.lower())
                                break
                    else:
                        # 未设定正筛的关键词，按默认正筛规则
                        matched_met = default_bind_trigger_to_metric(trigger)
                        if matched_met:
                            # 如果按默认规则定位到了另一个metric，弃之
                            if matched_met.name == met.name:
                                n_chk_match = 1
                                print("matched default: " + matched_met.name)
                            else:
                                print("skip matched default: " + matched_met.name)
                                # 因n_chk_match=0接下来会进入下一次for循环继续找
                    # 反筛
                    if n_chk_match:
                        met_kws2 = matched_met.kw_exclude.replace(' ', '').\
                                       replace('|', ',').replace('，', ',')
                        if met_kws2.replace(',', ''):
                            for kw in met_kws2.split(','):
                                if kw and kw.lower() in trigger.expr.lower():
                                    n_chk_match = 0
                                    print("unmatched: " + kw.lower() + " -> "
                                          + trigger.expr.lower())
                                    break
                    # add
                    if n_chk_match:
                        matched_met.triggerList.add(trigger)
                        break

                # 未匹配到，一律归属到其它
                if not n_chk_match:
                    un_metric = Metric.objects.get(name__contains=u'其它')
                    un_metric.triggerList.add(trigger)
        except:
            pass

        host = None
        try:
            host = update_host(problem=p)
            res_dict["host update succeed"] += 1
        except:
            res_dict["host update failed"] += 1

        ins = None
        try:
            # ins = Instance.objects.get(name=p.instance, ip=p.ip)
            ins = Instance.objects.filter(name=p.instance, ip=p.ip).first()
        except Instance.DoesNotExist:
            try:
                ins = Instance.objects.create(name=p.instance, ip=p.ip)
                res_dict["instance succeed"] += 1
            except:
                res_dict["instance failed"] += 1

        try:
            host.instanceList.add(ins)
            res_dict["attach instance succeed"] += 1
        except:
            res_dict["attach instance failed"] += 1

        item = None
        try:
            # item = Item.objects.get(instance=ins, trigger=trigger)
            item = Item.objects.filter(instance=ins, trigger=trigger).first()
        except Item.DoesNotExist:
            try:
                res_dict["item new"] += 1
                item = Item.objects.create(instance=ins, trigger=trigger)
                res_dict["item succeed"] += 1
            except:
                res_dict["item failed"] += 1

        try:
            if not p.item_id:
                p.item_id = item.id
                p.save()
                res_dict["problem update succeed"] += 1
        except Exception as e:
            res_dict["problem update failed"] += 1
            return HttpResponse(str(res_dict) + '\n' + str(e))

    # return str(res_dict)
    return res_dict


def update_service_all(problem):
    try:
        service = HostService.objects.get(name='All')
        if problem.ip == "127.0.0.1":
            cur_host = Host.objects.get(hostname=problem.instance, ip=problem.ip)
        else:
            # cur_host = Host.objects.get(ip=problem.ip)
            cur_host = Host.objects.filter(ip=problem.ip).first()
        # cur_instance = Instance.objects.get(name=problem.instance, ip=problem.ip)
        cur_instance = Instance.objects.filter(name=problem.instance, ip=problem.ip).first()
        service.serverList.add(cur_host)
        service.instanceList.add(cur_instance)
    except Exception as e:
        print(str(e))


def update_host(problem):
    host = None
    try:
        if '127.0.0.1' == problem.ip:
            host = Host.objects.get(hostname=problem.instance)
        else:
            # host = Host.objects.get(ip=problem.ip)
            host = Host.objects.filter(ip=problem.ip).first()
            if not host.hostname or host.hostname.startswith(problem.ip):
                if problem.instance and not problem.instance.startswith(problem.ip):
                    # Host.objects.update(hostname=problem.instance,
                    #                     update_time=problem.create_time)       # 错？
                    host.hostname = problem.instance
                    host.update_time = problem.create_time
                    host.save()
    except Host.DoesNotExist:
        try:
            host = Host.objects.create(hostname=problem.instance, ip=problem.ip,
                                       create_time=problem.create_time)
        except:
            pass

    return host


def is_rule_effective(problem, rule):
    chk = 0
    # 判断是否启用
    if rule.is_active:
        chk += 1
    else:
        return 0

    # 判断严重级别是否符合
    if rule.r_severity <= problem.severity:
        chk += 1

    p_hosts = Host.objects.filter(ip=problem.ip)
    # for h in p_hosts:
    #     if not h.status or h.status == 1:
    #         # 只要一个状态为1或默认空，就认为该IP的主机（可能有多个重复）都正常使用中
    #         chk += 1
    #         break
    # 判断系统
    if not rule.r_sys:
        chk += 1
    else:
        all_syshosts = []
        allsvc = rule.r_sys.serviceList.all()
        for svc in allsvc:
            svc_hosts = svc.serverList.all()
            all_syshosts.extend(svc_hosts)

        all_syshosts = list(set(all_syshosts))
        for h in p_hosts:
            if h in all_syshosts:
                chk += 1
                break

    # 判断分组
    if not rule.r_group:
        chk += 1
    else:
        all_svchosts = rule.r_group.serverList.all()
        for h in p_hosts:
            if h in all_svchosts:
                chk += 1
                break

    # 判断触发器
    if not rule.triggerList.all():
        chk += 1
    else:
        trigger = Item.objects.get(id=problem.item_id).trigger
        if trigger in rule.triggerList.all():
            chk += 1

    # 判断主机
    if not rule.hostList.all():
        chk += 1
    else:
        for h in p_hosts:
            if h in rule.hostList.all():
                chk += 1
                break

    # 判断关键词是否匹配
    if not rule.keywords:
        chk += 1
    else:
        kws = rule.keywords.replace(' ', '').replace('|', ',').replace('，', ',')
        if not kws.replace(',', ''):
            chk += 1
        else:
            for kw in kws.split(','):
                if kw and kw in problem.expr:
                    chk += 1
                    break

    if 7 == chk:
        if rule.is_negative:
            return 2
        else:
            return 1
    else:
        return 0


def get_all_effective_rules000(problem):
    """
    弃用的
    """
    rules = []
    for rule in Rule.objects.all():
        if is_rule_effective(problem, rule):
            rules.append(rule)

    return rules


def get_all_effective_rules(problem):
    for rule in Rule.objects.all():
        if 1 == is_rule_effective(problem, rule):
            yield rule


def get_all_ineffective_rules(problem):
    for rule in Rule.objects.all():
        if 2 == is_rule_effective(problem, rule):
            yield rule


def alert_user(data, problem):
    # p_host = Host.objects.get(ip=data.get('ip'))
    p_host = Host.objects.filter(ip=data.get('ip')).first()
    if p_host:
        data.setdefault("host_id", p_host.id)
        data.setdefault("sys_id", "")
        data.setdefault("plat_id", "")
        data.setdefault("met_name", u"无")
        met = Metric.objects.filter(triggerList=problem.item.trigger).first()
        if met:
            sp_index = str(met.name).index(" ") if " " in met.name else 0
            data["met_name"] = str(met.name)[sp_index:].strip()
            if u"网络" in met.name:
                find_plat, find_sys, find_svc, host = get_host_group_info(p_host.id)
                data["sys_id"] = find_sys.id if find_sys else ""
                data["plat_id"] = find_plat.id if find_plat else ""
    else:
        # host未创建成功也不处理
        pass

    positive_rules = get_all_effective_rules(problem)
    negative_rules = get_all_ineffective_rules(problem)
    users = set(UserInfo.objects.filter(
        is_alert_enabled=True,
        ruleset__ruleset__in=positive_rules).exclude(
        ruleset__ruleset__in=negative_rules))
    try:
        alert_task(data, users)
        Notification.objects.create(
            ip=data.get('ip')[:39],
            expr=data.get("expr"),
            desc=data.get('desc')[:255],
            severity=int(data.get('severity')),
            status=1 if "resolved" == data.get("status") else 0,
            source=data.get("source"),
            name=data.get("name"),
            instance=data.get("instance"),
            receivers=",".join([u.username for u in users]),
            create_time=datetime.datetime.strptime(data.get('create_time'),
                                                   "%Y-%m-%d %H:%M:%S")
        )
    except Exception as e:
        print(str(e))


@csrf_exempt
@token_verify()
def received_problem(request):
    try:
        data = json.loads(request.body)
        # 先改写一下 ip 和 instance名称
        data["ip"] = data.get('ip')[:39]
        if data.get('instance') and data["instance"].startswith(data.get('ip')):
            try:
                h = Host.objects.filter(ip=data.get('ip'))[0]
                data["instance"] = h.hostname
            except:
                pass

        # 判断是否需要通知并记录
        alert_chk = False
        p_instance = data.get('instance')
        p_ip = data.get('ip')
        p_hosts = Host.objects.filter(ip=data.get('ip'))
        if not p_hosts:
            alert_chk = True
        else:
            for h in p_hosts:
                # 未设置状态 或使用中状态
                if not h.status or h.status == 1:
                    alert_chk = True
                    break
        if not alert_chk:
            return HttpResponse("Not in use: no need to notify.")

        if data.get('update_time'):
            data.setdefault("status", "resolved")
            target_problems = Problem.objects.filter(ip=p_ip,
                                                     status=0,
                                                     instance=p_instance,
                                                     source=data.get('source'),
                                                     expr=data.get('expr')).annotate(
                latest_date=Max('create_time')).order_by('-latest_date')
            problem0 = target_problems[0]
            t = datetime.datetime.strptime(data.get('update_time'), "%Y-%m-%d %H:%M:%S")
            target_problems.update(status=1, update_time=t)
            t_local = problem0.create_time + datetime.timedelta(hours=8)
            data.setdefault("create_time", t_local.strftime("%F %T"))
            data["status_code"] = 1
            alert_user(data, problem0)
            return HttpResponse("Resolved: {} {}".format(p_instance, p_ip))
        else:
            data.setdefault("status", "firing")
            data["status_code"] = 0
            data["severity"] = int(data.get('severity'))
            problem = Problem.objects.create(status=0,
                                             name=data.get('name'),
                                             ip=p_ip,
                                             source=data.get('source') or 0,
                                             severity=data.get('severity'),
                                             desc=data.get('desc')[:255],
                                             expr=data.get('expr'),
                                             create_time=datetime.datetime.strptime(
                                                 data.get('create_time'),
                                                 "%Y-%m-%d %H:%M:%S"),
                                             instance=p_instance)
            update_from_new_problem(problem)  # 更新host,ins,trigger,item,problem等
            update_service_all(problem)  # 更新名称为All的分组
            alert_user(data, problem)   # 发通知
            return HttpResponse("Received: {} {}".format(problem.instance, problem.ip))
    except Exception as e:
        return HttpResponse(e.message)
