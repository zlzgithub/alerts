#! /usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from django import forms
from django.forms.widgets import *
from .models import Host, Idc, HostGroup, Cabinet, HostService, ServiceSystem, SystemGroup, Rule
from monitor.models import Problem, Item, Trigger, Instance


class AssetForm(forms.ModelForm):
    class Meta:
        model = Host
        exclude = ("id",)
        widgets = {
            'hostname': TextInput(
                attrs={'class': 'form-control', 'style': 'width:450px;', 'placeholder': u'必填项'}),
            'ip': TextInput(
                attrs={'class': 'form-control', 'style': 'width:450px;', 'placeholder': u'必填项'}),
            'other_ip': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'group': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'asset_no': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'asset_type': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'status': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'os': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'vendor': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'up_time': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'cpu_model': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'cpu_num': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'memory': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'disk': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'sn': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'idc': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'position': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;',
                                         'placeholder': u'物理机写位置，虚机写宿主'}),
            'memo': Textarea(
                attrs={'rows': 4, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),
            'create_time': forms.DateTimeInput(attrs={'class': 'form-control',
                                                      'style': 'width:450px;'}),
            'update_time': forms.DateTimeInput(attrs={'class': 'form-control',
                                                      'style': 'width:450px;'}),
        }


class IdcForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(IdcForm, self).clean()
        value = cleaned_data.get('ids')
        try:
            Idc.objects.get(name=value)
            # self._errors['ids'] = self.error_class(["%s的信息已经存在" % value])
        except Idc.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = Idc
        exclude = ("id",)

        widgets = {
            'ids': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'address': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'tel': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'contact': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'contact_phone': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'ip_range': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'jigui': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'bandwidth': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        }


class GroupForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(GroupForm, self).clean()
        return cleaned_data

    class Meta:
        model = HostGroup
        exclude = ("id",)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'desc': Textarea(
                attrs={'rows': 4, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),
        }


class ProblemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ProblemForm, self).clean()
        name = cleaned_data.get('name')
        try:
            Problem.objects.filter(name=name)
        except Problem.DoesNotExist:
            pass
        return cleaned_data

    class Meta:
        model = Problem
        exclude = ("id", "item")

        widgets = {
            'name': Textarea(
                attrs={'rows': 2, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),
            'ip': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'instance': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'severity': forms.Select(choices=((0, u'信息'),
                                              (1, u'低'),
                                              (2, u'中'),
                                              (3, u'高')),
                                     attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'status': forms.Select(choices=((0, u'未确认'),
                                            (1, u'已确认')),
                                   attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'source': forms.Select(choices=((0, u'Zabbix'),
                                            (1, u'Prometheus'),
                                            (2, u'ELK')),
                                   attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'create_time': forms.DateTimeInput(attrs={'class': 'form-control',
                                                      'style': 'width:450px;'}),
            # 'update_time': forms.DateTimeInput(
            #     attrs={'class': 'form-control', 'type': 'dateandtime', 'style': 'width: 450px;'}),
            'update_time': forms.DateTimeInput(attrs={'class': 'form-control',
                                                      'style': 'width:450px;'}),

            'expr': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'desc': Textarea(
                attrs={'rows': 4, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),
        }


class ServiceForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ServiceForm, self).clean()
        return cleaned_data

    class Meta:
        model = HostService
        exclude = ("id",)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'desc': Textarea(
                attrs={'rows': 4, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),
        }


class SystemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(SystemForm, self).clean()
        return cleaned_data

    class Meta:
        model = ServiceSystem
        exclude = ("id",)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'desc': Textarea(
                attrs={'rows': 4, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),
        }


class SystemGroupForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(SystemGroupForm, self).clean()
        return cleaned_data

    class Meta:
        model = SystemGroup
        exclude = ("id",)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'desc': Textarea(
                attrs={'rows': 4, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),
        }


class CabinetForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(CabinetForm, self).clean()
        return cleaned_data

    class Meta:
        model = Cabinet
        exclude = ("id",)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'idc': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'desc': Textarea(
                attrs={'rows': 4, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),

        }


class ItemForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ItemForm, self).clean()
        return cleaned_data

    class Meta:
        model = Item
        exclude = ("id",)

        # widgets = {
        #     'instance': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        #     'ip': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        #     'trigger': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        # }

        widgets = {
            'instance': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'trigger': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        }


class RuleForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(RuleForm, self).clean()
        # cleaned_data.setdefault('editor', )
        return cleaned_data

    class Meta:
        model = Rule
        exclude = ("id", "editor")

        # widgets = {
        #     'instance': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        #     'ip': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        #     'trigger': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        # }

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            # 'editor': TextInput(
            #     attrs={'class': 'form-control', 'style': 'width:450px;', 'readonly': True}),
            'r_severity': forms.Select(choices=((0, u'不限'),
                                                (1, u'低'),
                                                (2, u'中'),
                                                (3, u'高'),
                                                (10, u'不通知')),
                                       attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'r_group': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'r_sys': Select(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'keywords': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;',
                                         'placeholder': u'多个以逗号、空格或竖线分隔'}),
            'is_negative': forms.Select(choices=((False, u'放行'), (True, u'拦截')),
                                        attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'is_active': forms.Select(choices=((False, u'禁用'), (True, u'启用')),
                                      attrs={'class': 'form-control', 'style': 'width:450px;'}),
        }


class InstanceForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(InstanceForm, self).clean()
        return cleaned_data

    class Meta:
        model = Instance
        exclude = ("id", "update_time")

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'name2': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'ip': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            # 'update_time': forms.DateTimeInput(attrs={'class': 'form-control',
            #                                           'style': 'width:450px;'}),
        }


class TriggerForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(TriggerForm, self).clean()
        return cleaned_data

    class Meta:
        model = Trigger
        exclude = ("id",)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'expr': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
        }
