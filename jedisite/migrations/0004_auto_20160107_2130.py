# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0003_auto_20160107_2001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameaccount',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
