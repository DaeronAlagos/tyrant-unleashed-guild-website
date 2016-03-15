# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-26 20:54
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0027_auto_20160226_2048'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameaccount',
            name='inventory',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=''),
            preserve_default=False,
        ),
    ]
