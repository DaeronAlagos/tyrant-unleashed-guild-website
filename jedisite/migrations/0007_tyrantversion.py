# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0006_auto_20160108_2243'),
    ]

    operations = [
        migrations.CreateModel(
            name='TyrantVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('salt', models.CharField(max_length=10)),
            ],
        ),
    ]
