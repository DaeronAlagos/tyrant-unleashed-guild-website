# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0009_delete_tyrantversion'),
    ]

    operations = [
        migrations.CreateModel(
            name='TyrantSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=256)),
            ],
        ),
    ]
