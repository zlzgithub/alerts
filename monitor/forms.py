#! /usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from django.forms.widgets import *
from monitor.models import Metric


class MetricForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(MetricForm, self).clean()
        return cleaned_data

    class Meta:
        model = Metric
        exclude = ("id",)

        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;'}),
            'kw_include': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;',
                                           'placeholder': u'多个以逗号、空格或竖线分隔'}),
            'kw_exclude': TextInput(attrs={'class': 'form-control', 'style': 'width:450px;',
                                           'placeholder': u'多个以逗号、空格或竖线分隔'}),
            'desc': Textarea(
                attrs={'rows': 4, 'cols': 15, 'class': 'form-control', 'style': 'width:450px;'}),
        }
