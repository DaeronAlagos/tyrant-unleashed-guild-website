# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-30 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0019_auto_20160130_1939'),
    ]

    operations = [
        migrations.RenameField(
            model_name='decks',
            old_name='structures',
            new_name='enemy_structures',
        ),
        migrations.AddField(
            model_name='decks',
            name='friendly_structures',
            field=models.CharField(default='', max_length=60),
            preserve_default=False,
        ),
    ]