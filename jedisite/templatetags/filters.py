from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(is_safe=True)
def is_in(val, obj):
    return val in unicode(obj)


@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)

    except:
        return False

    return user.groups.filter(name=group_name).exists()
