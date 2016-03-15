# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0008_tyrantversion_client_version'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TyrantVersion',
        ),
    ]
