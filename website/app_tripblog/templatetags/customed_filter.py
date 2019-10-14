from django import template

'''register filter'''

register = template.Library()

@register.filter
def get_range(value):
    return range(value)

@register.filter
def get_listitem(list, index):
    return list[index]