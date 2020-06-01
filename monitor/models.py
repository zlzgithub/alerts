#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class Instance(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"实例名称")
    name2 = models.CharField(max_length=255, verbose_name=u"实例别名")
    ip = models.GenericIPAddressField(u"所属IP", max_length=15)
    update_time = models.DateTimeField(verbose_name=u"更新时间", blank=True, null=True)

    def __unicode__(self):
        return self.name + " | " + self.ip


class Trigger(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"触发器名称")
    expr = models.CharField(max_length=255, verbose_name=u"触发条件")

    def __unicode__(self):
        return self.name + " | " + self.expr


class Item(models.Model):
    instance = models.ForeignKey(Instance, related_name="instance_itemList", verbose_name=u"实例",
                                 on_delete=models.SET_NULL, null=True, blank=True)
    trigger = models.ForeignKey(Trigger, related_name="trigger_itemList", verbose_name=u"触发器",
                                on_delete=models.SET_NULL, null=True, blank=True)

    def __unicode__(self):
        return ((self.instance.name + " | " + self.instance.ip)
                if self.instance else "No instance") + " | " + \
               ((self.trigger.name + " | " + self.trigger.expr)
                if self.trigger else "No trigger")


class Metric(models.Model):
    name = models.CharField(u"指标名称", max_length=30, unique=True)
    desc = models.CharField(u"描述", max_length=100, blank=True)
    kw_include = models.CharField(u"包含关键词", max_length=255, blank=True)
    kw_exclude = models.CharField(u"排除关键词", max_length=255, blank=True)
    triggerList = models.ManyToManyField(
        Trigger,
        blank=True,
        verbose_name=u"触发器"
    )

    def __unicode__(self):
        return self.name


class Problem(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"问题名")
    ip = models.GenericIPAddressField(u"IP", max_length=15)
    instance = models.CharField(max_length=255, verbose_name=u"实例名")
    severity = models.IntegerField(default=0, verbose_name=u"级别")
    status = models.IntegerField(default=0, verbose_name=u"处理状态")
    source = models.IntegerField(default=0, verbose_name=u"来源")
    desc = models.CharField(u"问题详情", max_length=255, blank=True)
    create_time = models.DateTimeField(verbose_name=u"创建时间", blank=True, null=True)
    update_time = models.DateTimeField(verbose_name=u"更新时间", blank=True, null=True)
    expr = models.CharField(max_length=255, verbose_name=u"表达式", null=True)
    item = models.ForeignKey(Item, related_name="item_problemList", verbose_name=u"监控项",
                             on_delete=models.SET_NULL, null=True,
                             blank=True)

    def __unicode__(self):
        return self.name


class Notification(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"通知名")
    ip = models.GenericIPAddressField(u"IP", max_length=15)
    instance = models.CharField(max_length=255, verbose_name=u"实例名")
    severity = models.IntegerField(default=0, verbose_name=u"级别")
    status = models.IntegerField(default=0, verbose_name=u"处理状态")
    source = models.IntegerField(default=0, verbose_name=u"来源")
    desc = models.CharField(u"问题详情", max_length=255, blank=True)
    expr = models.CharField(max_length=255, verbose_name=u"表达式", null=True)
    receivers = models.CharField(max_length=255, verbose_name=u"接收人")
    create_time = models.DateTimeField(verbose_name=u"通知时间", blank=True, null=True)

    def __unicode__(self):
        return self.name

    def receivers_as_list(self):
        return self.receivers.split(',')
