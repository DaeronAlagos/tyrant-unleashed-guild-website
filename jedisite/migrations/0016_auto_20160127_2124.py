# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-27 21:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0015_auto_20160127_2027'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='decks',
            name='type',
        ),
        migrations.AddField(
            model_name='decks',
            name='bge',
            field=models.CharField(default='bge', max_length=50),
            preserve_default=False,
        ),
    ]
