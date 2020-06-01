#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from monitor import system, manage, api, health, problem, health_api

urlpatterns = [
    url(r'^index/$', system.index, name='system_index'),
    url(r'^syslink/$', system.syslink_index, name='syslink'),
    url(r'^syshost/$', system.monitor_index, name='monitor'),

    # systems
    url(r'^health/metric/systems/$', health.metric_overview_systems,
        name='metric_overview_systems'),
    # services
    url(r'^health/metric/services/$', health.metric_overview_services,
        name='metric_overview_services'),
    # system -> hosts
    url(r'^health/metric/system/(?P<system_id>\d+)/hosts/$', health.metric_index_hosts,
        name='metric_index_hosts'),
    # service -> hosts
    url(r'^health/metric/service/(?P<service_id>\d+)/hosts/$', health.metric_service_index_hosts,
        name='metric_service_index_hosts'),
    # (system ->) host -> problems
    url(r'^health/metric/host/(?P<host_id>.+)/problems/$', health.metric_index_problems,
        name='health_metric_index_problems'),
    # (service ->) host -> problems
    url(r'^health/metric/service/host/(?P<host_id>.+)/problems/$',
        health.metric_service_index_problems, name='health_metric_service_index_problems'),

    # problems
    url(r'^health/problems/$', health.overview_problems, name='health_overview_problems'),
    # problem
    url(r'^health/problem/(?P<problem_id>\d+)/$', health.problem, name='health_problem'),

    # notifications
    url(r'^health/notifications/$', health.overview_notifications,
        name='health_overview_notifications'),
    # notification
    url(r'^health/notification/(?P<notification_id>\d+)/$', health.notification,
        name='health_notification'),

    # by server ############################
    # systems
    url(r'^health/systems/$', health.overview_systems, name='health_overview_systems'),
    # groups
    url(r'^health/services/$', health.overview_services, name='health_overview_services'),
    # hosts
    url(r'^health/hosts/$', health.overview_hosts, name='health_overview_hosts'),

    # system -> groups
    url(r'^health/system/(?P<system_id>\d+)/services/$', health.index_services,
        name='health_index_services'),
    # group -> hosts
    url(r'^health/service/(?P<service_id>\d+)/hosts/$', health.index_hosts,
        name='health_index_hosts'),
    # host -> problems
    url(r'^health/host/(?P<host_id>.+)/problems/$', health.index_problems,
        name='health_index_problems'),

    # #####################################
    # get APIs
    url(r'^health/getproblems/$', health_api.get_problems_data, name='get_problems_data'),
    url(r'^health/getnotifications/$', health_api.get_notifications_data, name='get_notifications_data'),

    url(r'^health/metric/system/(?P<system_id>\d+)/gethostspiedata/$',
        health_api.get_metric_hosts_pie_data,
        name='get_metric_hosts_pie_data'),
    url(r'^health/metric/service/(?P<service_id>\d+)/gethostspiedata/$',
        health_api.get_metric_service_hosts_pie_data,
        name='get_metric_service_hosts_pie_data'),
    url(r'^health/metric/host/getseveritypiedata/(?P<s_id>\d+)/$',
        health_api.get_metric_severity_pie_data,
        name='get_metric_severity_pie_data'),

    url(r'^health/systems/getlatest5/$', health_api.get_latest5_hosts,
        name='get_latest5_hosts'),
    url(r'^health/systems/data/$', health_api.api_get_metric_overview_systems_data,
        name='api_get_metric_overview_systems_data'),
    url(r'^health/systems/ctp/$', health_api.get_systems_problems_data,
        name='get_systems_problems_data'),
    url(r'^health/systems/ctphisto/$', health_api.get_systems_problems_data_histo,
        name='get_systems_problems_data_histo'),
    url(r'^health/systems/ctpcur/$', health_api.get_systems_problems_data_cur,
        name='get_systems_problems_data_cur'),
    url(r'^health/systems/ctphis/$', health_api.get_systems_problems_data_his,
        name='get_systems_problems_data_his'),
    url(r'^health/systems/htmltags/$', health_api.get_metric_overview_page_tags,
        name='get_metric_overview_page_tags'),

    url(r'^health/system/(?P<system_id>\d+)/ctp/$', health_api.get_system_problems_data,
        name='get_system_problems_data'),
    url(r'^health/system/(?P<system_id>\d+)/ctp2/$', health_api.get_system_problems_data2,
        name='get_system_problems_data2'),
    url(r'^health/system/(?P<system_id>\d+)/ctpcur/$', health_api.get_system_problems_data_cur,
        name='get_system_problems_data_cur'),
    url(r'^health/system/(?P<system_id>\d+)/ctphis/$', health_api.get_system_problems_data_his,
        name='get_system_problems_data_his'),

    url(r'^health/service/(?P<service_id>\d+)/ctp/$', health_api.get_service_problems_data,
        name='get_service_problems_data'),
    url(r'^health/service/(?P<service_id>\d+)/ctpcur/$',
        health_api.get_service_problems_data_cur,
        name='get_service_problems_data_cur'),
    url(r'^health/service/(?P<service_id>\d+)/ctphis/$',
        health_api.get_service_problems_data_his,
        name='get_service_problems_data_his'),

    url(r'^health/host/(?P<host_id>.+)/ctp/$', health_api.get_host_problems_data,
        name='get_host_problems_data'),
    url(r'^health/host/(?P<host_id>.+)/ctpcur/$', health_api.get_host_problems_data_cur,
        name='get_host_problems_data_cur'),
    url(r'^health/host/(?P<host_id>.+)/ctphis/$', health_api.get_host_problems_data_his,
        name='get_host_problems_data_his'),

    # monitor
    url(r'^received/sys/info/$', api.received_sys_info, name='received_sys_info'),
    url(r'^manage/delall/$', manage.drop_sys_info, name='drop_all'),
    url(r'^manage/delrange/(?P<timing>[0-9])/$', manage.del_monitor_data, name='del_monitor_data'),
    url(r'^manage/delsyslinkdata/(?P<timing>[0-9])/$', manage.del_syslink_data, name='del_syslink_data'),
    url(r'^manage/$', manage.index, name='monitor_manage'),

    url(r'^received/syslink/info/$', api.received_syslink_info, name='received_syslink_info'),
    url(r'^received/syslink/data/$', api.received_syslink_data, name='received_syslink_data'),
    url(r'^syslink/tree/$', system.syslink_tree_node, name='syslink_tree'),
    url(r'^syslink/(?P<item_type>.+)/(?P<item_id>.+)/$', system.syslink_info, name='syslink_info'),
    url(r'^getsyslinkdata/(?P<item_type>.+)/(?P<item_id>.+)/$', system.get_syslink_data, name='get_syslink_data'),

    url(r'^syshost/tree/$', system.syshost_tree_node, name='syshost_tree'),
    url(r'^syshost/(?P<hostname>.+)/(?P<timing>\d+)/$', system.syshost_info, name='syshost_info'),
    url(r'^getsyshostdata/cpu/(?P<hostname>.+)/(?P<timing>\d+)/$', system.get_cpu, name='get_cpu'),
    url(r'^getsyshostdata/mem/(?P<hostname>.+)/(?P<timing>\d+)/$', system.get_mem, name='get_mem'),
    url(r'^getsyshostdata/disk/(?P<hostname>.+)/(?P<timing>\d+)/(?P<partition>\d+)/$', system.get_disk,
        name='get_disk'),
    url(r'^getsyshostdata/net/(?P<hostname>.+)/(?P<timing>\d+)/(?P<net_id>\d+)/$', system.get_net,
        name='get_net'),

    # problem
    url(r'^problemadd/$', problem.problem_add, name='problem_add'),
    url(r'^problemedit/(?P<problem_id>\d+)/$', problem.problem_edit, name='problem_edit'),
    url(r'^confirmproblems/$', problem.confirm_problems, name='confirm_problems'),
    url(r'^clearproblems/$', problem.clear_problems, name='clear_problems'),
    url(r'^delproblems/$', problem.del_problems, name='del_problems'),
    url(r'^problemdel/(?P<problem_id>\d+)/$', problem.problem_del, name='problem_del'),
    url(r'^received/problem/$', api.received_problem, name='received_problem'),

    # test
    url(r'^problem/refresh/$', api.refresh_item_id__isnull_problems, name='refresh_problem'),
]
