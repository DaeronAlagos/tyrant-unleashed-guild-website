# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-01 19:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0029_auto_20160226_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decks',
            name='bge',
            field=models.CharField(max_length=128),
        ),
    ]
