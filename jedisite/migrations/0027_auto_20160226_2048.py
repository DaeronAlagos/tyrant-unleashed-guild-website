# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-26 20:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0026_auto_20160226_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameaccount',
            name='kong_name',
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='gameaccount',
            name='name',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]