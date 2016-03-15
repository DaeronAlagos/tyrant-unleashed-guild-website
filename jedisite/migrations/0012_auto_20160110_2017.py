# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0011_auto_20160110_1954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameaccount',
            name='canvas',
            field=models.URLField(unique=True, max_length=1024),
        ),
    ]
