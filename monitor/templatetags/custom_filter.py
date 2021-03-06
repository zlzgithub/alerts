from django import template
from django.utils.datastructures import OrderedDict

register = template.Library()


@register.filter(name='sort2')
def listsort2(value):
    if isinstance(value, dict):
        new_dict = OrderedDict()
        key_list = sorted(value.keys())
        for key in key_list:
            new_dict[key] = value[key]
        return new_dict
    elif isinstance(value, list):
        return sorted(value)
    else:
        return value
    listsort.is_safe = True


@register.filter(name='sort')
def listsort(value):
    if isinstance(value, list):
        return sorted(value, key=lambda k: k[0])
    else:
        return value
