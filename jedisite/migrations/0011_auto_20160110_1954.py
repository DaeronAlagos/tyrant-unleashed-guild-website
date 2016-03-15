# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0010_tyrantsettings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameaccount',
            name='postdata',
            field=models.URLField(max_length=1024),
        ),
    ]
