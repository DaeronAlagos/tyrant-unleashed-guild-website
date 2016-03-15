# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0007_tyrantversion'),
    ]

    operations = [
        migrations.AddField(
            model_name='tyrantversion',
            name='client_version',
            field=models.PositiveSmallIntegerField(default=56),
        ),
    ]
