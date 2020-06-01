#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time
# from datetime import datetime
from datetime import datetime

from django.contrib.auth.decorators import login_required
from accounts.permission import permission_verify
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from cmdb.models import Host, Idc, HostGroup, HostService, SystemGroup, ServiceSystem
from monitor.api import GetSysData, GetSyslinkData

TIME_SECTOR = (
            3600,
            3600*3,
            3600*5,
            86400,
            86400*3,
            86400*7,
)


def log(msg):
    print(msg)
    ts = datetime.now().strftime("%F %T")
    with open('/tmp/alerts_mylog.log', 'a') as f:
        f.write("[{}] {}\n".format(ts, msg))


def get_edge_path(timing=300):
    edge_path_list = []
    mongo_edge_path = GetSyslinkData(timing, no=5000)
    for doc in mongo_edge_path.get_data():
        # del doc["_id"]
        edge_path_list.append(doc)
    return edge_path_list


# @login_required
# @csrf_exempt
@login_required()
@permission_verify()
def get_cpu(request, hostname, timing):
    data_time = []
    cpu_percent = []
    range_time = TIME_SECTOR[int(timing)]
    cpu_data = GetSysData(hostname, "cpu", range_time)

    for doc in cpu_data.get_data():
        unix_time = doc['timestamp']
        times = time.localtime(unix_time)
        dt = time.strftime("%m%d-%H:%M", times)
        data_time.append(dt)
        c_percent = doc['cpu']['percent']
        cpu_percent.append(c_percent)
    data = {"data_time": data_time, "cpu_percent": cpu_percent}
    return HttpResponse(json.dumps(data))


@login_required()
@permission_verify()
def get_mem(request, hostname, timing):
    data_time = []
    mem_percent = []
    range_time = TIME_SECTOR[int(timing)]
    mem_data = GetSysData(hostname, "mem", range_time)
    for doc in mem_data.get_data():
        unix_time = doc['timestamp']
        times = time.localtime(unix_time)
        dt = time.strftime("%m%d-%H:%M", times)
        data_time.append(dt)
        m_percent = doc['mem']['percent']
        mem_percent.append(m_percent)
    data = {"data_time": data_time, "mem_percent": mem_percent}
    return HttpResponse(json.dumps(data))


@login_required()
@permission_verify()
def get_disk(request, hostname, timing, partition):
    data_time = []
    disk_percent = []
    disk_name = ""
    range_time = TIME_SECTOR[int(timing)]
    disk = GetSysData(hostname, "disk", range_time)
    for doc in disk.get_data():
        unix_time = doc['timestamp']
        times = time.localtime(unix_time)
        dt = time.strftime("%m%d-%H:%M", times)
        data_time.append(dt)
        d_percent = doc['disk'][int(partition)]['percent']
        disk_percent.append(d_percent)
        if not disk_name:
            disk_name = doc['disk'][int(partition)]['mountpoint']
    data = {"data_time": data_time, "disk_name": disk_name, "disk_percent": disk_percent}
    return HttpResponse(json.dumps(data))


@login_required()
@permission_verify()
def get_net(request, hostname, timing, net_id):
    data_time = []
    nic_in = []
    nic_out = []
    nic_name = ""
    range_time = TIME_SECTOR[int(timing)]
    net = GetSysData(hostname, "net", range_time)
    for doc in net.get_data():
        unix_time = doc['timestamp']
        times = time.localtime(unix_time)
        dt = time.strftime("%m%d-%H:%M", times)
        data_time.append(dt)
        in_ = doc['net'][int(net_id)]['traffic_in']
        out_ = doc['net'][int(net_id)]['traffic_out']
        nic_in.append(in_)
        nic_out.append(out_)
        if not nic_name:
            nic_name = doc['net'][int(net_id)]['nic_name']
    data = {"data_time": data_time, "nic_name": nic_name, "traffic_in": nic_in, "traffic_out": nic_out}
    return HttpResponse(json.dumps(data))


@login_required()
@permission_verify()
def index(request):
    return HttpResponseRedirect(reverse('metric_overview_systems'))


@login_required()
@permission_verify()
def monitor_index(request):
    return render(request, "monitor/index.html", locals())


@login_required()
@permission_verify()
def syslink_index(request):
    return render(request, "monitor/index_syslink.html", locals())


@login_required()
@permission_verify()
def syshost_info(request, hostname, timing):
    # 传递磁盘号给前端JS,用以迭代分区图表
    disk = GetSysData(hostname, "disk", 3600, 1)
    disk_data = disk.get_data()
    partitions_len = []
    for d in disk_data:
        p = len(d["disk"])
        for x in range(p):
            partitions_len.append(x)
    # 传递网卡号给前端,用以迭代分区图表
    net = GetSysData(hostname, "net", 3600, 1)
    nic_data = net.get_data()
    nic_len = []
    for n in nic_data:
        p = len(n["net"])
        for x in range(p):
            nic_len.append(x)
    return render(request, "monitor/host_info.html", locals())


@login_required()
@permission_verify()
def syslink_info(request, item_type, item_id):
    if "platform" == item_type:
        item = SystemGroup.objects.get(id=item_id)
    elif "system" == item_type:
        item = ServiceSystem.objects.get(id=item_id)
    return render(request, "monitor/workflow.html", locals())


def get_label(lab):
    label = str(lab).decode('utf-8')
    new_lab = label
    n_len = len(label)
    if n_len/10 >= 3:
        if n_len % 10 < 6:
            new_lab = label[:10] + '\n  ' + label[10:20] + '\n  ' + label[20:]
        else:
            new_lab = label[:10] + '\n  ' + label[10:20] + '\n  ' + label[20:30] + \
                               '\n  ' + label[30:]
    elif n_len/10 >= 2:
        if n_len % 10 < 6:
            new_lab = label[:10] + '\n  ' + label[10:]
        else:
            new_lab = label[:10] + '\n  ' + label[10:20] + '\n  ' + label[20:]
    elif n_len/10 >= 1:
        if n_len % 10 < 6:
            new_lab = label
        else:
            new_lab = label[:10] + '\n  ' + label[10:]
    else:
        new_lab = label

    return new_lab


def get_d3_data(node_data, ts=360, expected_edge_data=None):
    NUM_MAX_NODES = 20
    node_ip_list = [node["ip"] for node in node_data if not str(node["ip"]).startswith('http')]
    edge_data = get_edge_path(ts)
    if expected_edge_data is not None and edge_data == expected_edge_data:
        return None

    new_node_data = []
    ip_list = []
    if len(node_data) < NUM_MAX_NODES:
        new_node_data = node_data
        ip_list = node_ip_list
    else:
        edge_ip_list = [e.get("from") for e in edge_data]
        edge_ip_list.extend([e.get("to") for e in edge_data])  # path的所有ip
        if edge_ip_list and node_ip_list:
            ip_list = list(set(edge_ip_list).intersection(set(node_ip_list)))  # 交集
            new_node_data = [d for d in node_data if d["ip"] in ip_list]

        if not new_node_data:
            new_node_data = node_data
        elif len(new_node_data) < NUM_MAX_NODES/2 + 1:
            # 补足NUM_MAX_NODES个节点
            xip_list = list(set(node_ip_list) - set(edge_ip_list))
            n_extra = NUM_MAX_NODES - len(new_node_data)
            extra_node_data_id = [x for x in xip_list[:n_extra]]
            extra_node_data = [d for d in node_data if d["ip"] in extra_node_data_id]
            new_node_data.extend(extra_node_data)

    new_edge_data = []
    linked_ips = []
    for e in edge_data:
        if e.get("from") in ip_list and e.get("to") in ip_list:
            new_edge_data.append(e)
            linked_ips.extend([e.get("from"), e.get("to")])

    node_msg = {}
    for d in new_node_data:
        node_msg[d["ip"]] = {"ip": d["ip"],
                             "id": d["id"],
                             "hostname": d["hostname"]}
        if d["ip"] in set(linked_ips):
            d["class"] = "type-Linked"

    edge_msg = {}
    for e in new_edge_data:
        k = "->".join([e.get("from"), e.get("to")])
        edge_msg[k] = ""

    new_edge_msg = edge_msg
    # 实际路径数与路径数据长度不一致时，每条路径只保留一个数据，另可考虑直接mongo筛选出不重复的数据
    if edge_msg and len(edge_msg) != len(new_edge_data):
        sorted_edge_data = sorted(sorted(new_edge_data, key=lambda da2: da2["to"], reverse=True),
                                  key=lambda da: da["from"], reverse=True)
        prev_e = {}
        rm_e = []
        for e in sorted_edge_data:
            if e.get("from") == prev_e.get("from") and e.get("to") == prev_e.get("to"):
                rm_e.append(e.get("_id"))
            else:
                prev_e = e
        all_e = [e.get("_id") for e in sorted_edge_data]
        res_e = list(set(all_e) - set(rm_e))
        new_edge_data = [e for e in sorted_edge_data if e.get("_id") in res_e]      # 耗时
        del sorted_edge_data
        del edge_msg

        new_edge_msg = {}
        for e in new_edge_data:
            k = "->".join([e.get("from"), e.get("to")])     # 默认title的格式: A->B
            if not e.get("title"):
                e["title"] = k
            new_edge_msg[k] = e

    # 删除_id对应的Object
    e_data = []
    for d in new_edge_data:
        del d["_id"]
        e_data.append(d)

    for k, v in new_edge_msg.items():
        if "_id" in v:
            del v["_id"]

    data = {
        "node_data": new_node_data,
        "node_msg": node_msg,
        "edge_data": e_data,
        "edge_msg": new_edge_msg,
        "total_node": len(node_data)
    }
    return data


@login_required()
@permission_verify()
def get_syslink_data(request, item_type, item_id):
    node_data = []
    if 'platform' == item_type:
        item = SystemGroup.objects.get(id=item_id)
        g_hosts = []
        for g_sys in item.systemList.all():
            for g_svc in g_sys.serviceList.all():
                host = g_svc.serverList.all()
                g_hosts.extend(host)
        g_hosts = set(g_hosts)
        node_data = [{"label": get_label(h.hostname),
                      "hostname": h.hostname,
                      "class": "type-Node",
                      "ip": h.ip,
                      "id": h.id} for h in g_hosts]

    if 'system' == item_type:
        item = ServiceSystem.objects.get(id=item_id)
        g_hosts = []
        for g_svc in item.serviceList.all():
            host = g_svc.serverList.all()
            g_hosts.extend(host)
        g_hosts = set(g_hosts)
        node_data = [{"label":  get_label(h.hostname) + '\n@' + h.ip,
                      "hostname": h.hostname,
                      "class": "type-Node",
                      "ip": h.ip,
                      "id": h.id} for h in g_hosts]
    data = get_d3_data(node_data, ts=360)
    expected_edge_data = data.get("edge_data") if data else None
    data0 = get_d3_data(node_data, ts=86400*7, expected_edge_data=expected_edge_data)
    if data0 is not None:
        for edge0 in data0.get("edge_msg"):
            if edge0 not in data.get("edge_msg"):
                data0.get("edge_msg")[edge0]["status"] = "lost"
        return HttpResponse(json.dumps(data0))

    return HttpResponse(json.dumps(data))


def sys_tree():
    host_node = []
    for plat in SystemGroup.objects.all():
        grp_systems = plat.systemList.all()
        g_sys_list = []
        for g_sys in grp_systems:
            sys_data = {'name': g_sys.name, 'url': "/monitor/syslink/system/{}/".format(g_sys.id), 'target': "myframe"}
            g_sys_list.append(sys_data)
        data = {"name": "平台: " + plat.name,
                'url': "/monitor/syslink/platform/{}/".format(plat.id),
                'target': "myframe",
                "open": True,
                "children": g_sys_list}
        del g_sys_list
        host_node.append(data)
    return host_node


@login_required
@csrf_exempt
def syslink_tree_node(request):
    all_node = sys_tree()
    return HttpResponse(json.dumps(all_node))


def host_tree():
    host_node = []
    for idc in Idc.objects.all():
        single_server_list = []
        for host in idc.host_set.all():
            if not host.cabinet_set.all():
                single_server_list.append({'name': host.hostname,
                                           'url': "/monitor/syshost/{}/0/".format(host.hostname), 'target':"myframe"})
        cabinet_list = []
        cabinets = idc.cabinet_set.all()
        for cabinet in cabinets:
            server_list = []
            servers = cabinet.serverList.all()
            for server in servers:
                server_data = {'name': server.hostname, 'url': "/monitor/syshost/{}/0/".format(server.hostname),
                               'target':"myframe"}
                server_list.append(server_data)
            cabinet_data = {'name': "机柜: " + cabinet.name, 'children': server_list}
            cabinet_list.append(cabinet_data)
            del server_list
        data = {"name": "机房: " + idc.name, "open": True, "children": cabinet_list + single_server_list }
        del cabinet_list
        host_node.append(data)
    return host_node


def group_tree():
    group_node = []
    for group in HostGroup.objects.all():
        server_list = []
        servers = group.serverList.all()
        for server in servers:
            server_data = {'name': server.hostname, 'url': "/monitor/syshost/{}/0/".format(server.hostname), 'target':"myframe"}
            server_list.append(server_data)
        group_data = {'name': "属组: " + group.name, "open": False, 'children': server_list}
        group_node.append(group_data)
        del server_list
    return group_node


def service_tree():
    service_node = []
    # for service in HostService.objects.exclude(name="All"):
    for service in HostService.objects.all():
        server_list = []
        servers = service.serverList.all()
        for server in servers:
            server_data = {'name': server.hostname, 'url': "/monitor/syshost/{}/0/".format(server.hostname), 'target':"myframe"}
            server_list.append(server_data)
        if server_list:
            service_data = {'name': "分组: " + service.name, "open": False, 'children': server_list}
            service_node.append(service_data)
            del server_list
    return service_node


@login_required
@csrf_exempt
def syshost_tree_node(request):
    # all_node = host_tree() + group_tree() + service_tree()
    all_node = host_tree() + service_tree()
    return HttpResponse(json.dumps(all_node))
