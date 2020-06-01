#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import url
from cmdb import api, idc, asset, group, cabinet, \
    service, system, systemgroup, item, instance, trigger, metric, rule

urlpatterns = [
    url(r'^asset/$', asset.asset, name='cmdb'),
    url(r'^assetadd/$', asset.asset_add, name='asset_add'),
    url(r'^assetdel/$', asset.asset_del, name='asset_del'),
    url(r'^assetimport/$', asset.asset_import, name='asset_import'),
    # url(r'^assetedit/(?P<ids>\d+)/$', asset.asset_edit, name='asset_edit'),
    url(r'^assetedit/(?P<asset_id>\d+)/$', asset.asset_edit, name='asset_edit'),
    url(r'^asset/detail/(?P<ids>\d+)/$', asset.server_detail, name='server_detail'),
    # url(r'^asset/save/$', asset.asset_save, name='asset_save'),

    url(r'^trigger/gettriggers/$', trigger.get_triggers_data, name='get_triggers_data'),
    url(r'^trigger/$', trigger.triggers, name='trigger_index'),
    url(r'^triggeradd/$', trigger.trigger_add, name='trigger_add'),
    url(r'^triggerdel/$', trigger.trigger_del, name='trigger_del'),
    url(r'^triggeredit/(?P<trigger_id>\d+)/$', trigger.trigger_edit, name='trigger_edit'),
    url(r'^trigger/detail/(?P<trigger_id>\d+)/$', trigger.trigger_detail, name='trigger_detail'),

    url(r'^item/$', item.items, name='item_index'),
    url(r'^itemadd/$', item.item_add, name='item_add'),
    url(r'^itemdel/$', item.item_del, name='item_del'),
    url(r'^itemedit/(?P<item_id>\d+)/$', item.item_edit, name='item_edit'),
    url(r'^item/detail/(?P<item_id>\d+)/$', item.item_detail, name='item_detail'),
    url(r'^item/getitems/$', item.get_items_data, name='get_items_data'),

    url(r'^rule/$', rule.rules, name='rule_index'),
    url(r'^ruleadd/$', rule.rule_add, name='rule_add'),
    url(r'^ruledel/$', rule.rule_del, name='rule_del'),
    url(r'^ruleedit/(?P<rule_id>\d+)/$', rule.rule_edit, name='rule_edit'),
    # url(r'^rule/detail/(?P<rule_id>\d+)/$', rule.rule_detail, name='rule_detail'),

    url(r'^instance/getinstances/$', instance.get_instances_data, name='get_instances_data'),
    url(r'^instance/$', instance.instance, name='instance_index'),
    url(r'^instanceadd/$', instance.instance_add, name='instance_add'),
    url(r'^instancedel/$', instance.instance_del, name='instance_del'),
    url(r'^instanceedit/(?P<instance_id>\d+)/$', instance.instance_edit, name='instance_edit'),
    url(r'^instance/detail/(?P<instance_id>\d+)/$', instance.instance_detail,
        name='instance_detail'),

    url(r'^metric/$', metric.metrics, name='metric_index'),
    url(r'^metricadd/$', metric.metric_add, name='metric_add'),
    url(r'^metricdel/$', metric.metric_del, name='metric_del'),
    url(r'^metricedit/(?P<metric_id>\d+)/$', metric.metric_edit, name='metric_edit'),
    # url(r'^metricitemlist/(?P<metric_id>\d+)/$', metric.item_list, name='metric_item_list'),
    url(r'^metricrelatedinfo/(?P<metric_id>\d+)/$', metric.related_info,
        name='metric_related_info'),

    url(r'^group/$', group.group, name='group'),
    url(r'^groupdel/$', group.group_del, name='group_del'),
    url(r'^groupadd/$', group.group_add, name='group_add'),
    url(r'^groupserverlist/(?P<group_id>\d+)/$', group.server_list, name='group_server_list'),
    url(r'^groupedit/(?P<group_id>\d+)/$', group.group_edit, name='group_edit'),
    # url(r'^group/save/$', group.group_save, name='group_save'),

    url(r'^service/$', service.service, name='service'),
    url(r'^servicedel/$', service.service_del, name='service_del'),
    url(r'^serviceadd/$', service.service_add, name='service_add'),
    url(r'^serviceserverlist/(?P<service_id>\d+)/$', service.server_list,
        name='service_server_list'),
    url(r'^serviceedit/(?P<service_id>\d+)/$', service.service_edit, name='service_edit'),

    url(r'^serviceedit2/(?P<service_id>\d+)/$', service.service_edit2, name='service_edit2'),
    url(r'^serviceedit3/(?P<service_id>\d+)/$', service.service_edit3, name='service_edit3'),
    url(r'^serviceedit4/(?P<service_id>\d+)/$', service.service_edit4, name='service_edit4'),
    url(r'^serviceedit5/(?P<service_id>\d+)/$', service.service_edit5, name='service_edit5'),

    url(r'^system/$', system.system, name='system'),
    url(r'^systemdel/$', system.system_del, name='system_del'),
    url(r'^systemadd/$', system.system_add, name='system_add'),

    url(r'^systemservicelist/(?P<system_id>\d+)/$', system.service_list,
        name='system_service_list'),
    url(r'^systemedit/(?P<system_id>\d+)/$', system.system_edit, name='system_edit'),

    url(r'^systemgroup/$', systemgroup.systemgroup, name='systemgroup'),
    url(r'^systemgroupdel/$', systemgroup.systemgroup_del, name='systemgroup_del'),
    url(r'^systemgroupadd/$', systemgroup.systemgroup_add, name='systemgroup_add'),
    url(r'^systemgroupsystemlist/(?P<systemgroup_id>\d+)/$', systemgroup.system_list,
        name='systemgroup_system_list'),
    url(r'^systemgroupedit/(?P<systemgroup_id>\d+)/$', systemgroup.systemgroup_edit,
        name='systemgroup_edit'),

    url(r'^cabinet/$', cabinet.cabinet, name='cabinet'),
    url(r'^cabinetdel/$', cabinet.cabinet_del, name='cabinet_del'),
    url(r'^cabinetadd/$', cabinet.cabinet_add, name='cabinet_add'),
    url(r'^cabinetserverlist/(?P<cabinet_id>\d+)/$', cabinet.server_list,
        name='cabinet_server_list'),
    url(r'^cabinetedit/(?P<cabinet_id>\d+)/$', cabinet.cabinet_edit, name='cabinet_edit'),

    url(r'^idc/$', idc.idc, name='idc'),
    url(r'^idcadd/$', idc.idc_add, name='idc_add'),
    url(r'^idcdel/$', idc.idc_del, name='idc_del'),
    url(r'^idcedit/(?P<idc_id>\d+)/$', idc.idc_edit, name='idc_edit'),
    url(r'^idccabinetlist/(?P<idc_id>\d+)/$', idc.cabinet_list, name='idc_cabinet_list'),
    url(r'^collect', api.collect, name='update_api'),
    url(r'^gethost/', api.get_host, name='get_host'),
    url(r'^getgroup/', api.get_group, name='get_group'),
    url(r'^nodestatus/(?P<ids>\d+)/$', asset.node_status, name='node_status'),
]
