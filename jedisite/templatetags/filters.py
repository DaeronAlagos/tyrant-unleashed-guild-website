from django import template
from django.contrib.auth.models import Group
from django.conf import settings
import re
from datetime import datetime, timedelta
from django.utils.timezone import utc, make_aware, datetime
from os import path

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


@register.filter
def strip_char(value):
    new_value = re.sub("[\s']", "", value)
    return new_value


@register.filter
def deck_age(value):

    now = datetime.utcnow().replace(tzinfo=utc)
    benchmark_modified = make_aware(
        datetime.fromtimestamp(
            int(
                path.getmtime(
                    path.join(
                        settings.BASE_DIR, 'utils/tuo/data/customdecks_benchmark.txt'
                    )
                )
            )
        ), utc
    )

    if value:
        if value < benchmark_modified:
            return "danger"
        elif now - value > timedelta(days=14):
            return "warning"
        else:
            return

    else:
        return "danger"
