# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0012_auto_20160110_2017'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameaccount',
            name='kong_name',
            field=models.CharField(default='kong_name', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='gameaccount',
            name='name',
            field=models.CharField(max_length=64),
        ),
    ]
