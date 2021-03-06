# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2017-03-30 21:34
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0039_auto_20160312_1510'),
    ]

    operations = [
        migrations.RenameField(
            model_name='warstats',
            old_name='enemy',
            new_name='enemy_guild',
        ),
        migrations.RemoveField(
            model_name='gameaccount',
            name='canvas',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_bot',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_officer',
        ),
        migrations.AddField(
            model_name='gameaccount',
            name='allow_command',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='line_name',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='warstats',
            name='friendly_guild',
            field=models.CharField(default='MasterJedis', max_length=64),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='benchmarks',
            name='score',
            field=models.DecimalField(decimal_places=3, max_digits=6),
        ),
        migrations.AlterField(
            model_name='decks',
            name='enemy_structures',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='decks',
            name='friendly_structures',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AlterField(
            model_name='decks',
            name='guild',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AlterField(
            model_name='gameaccount',
            name='inventory',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=64), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='gameaccount',
            name='postdata',
            field=models.CharField(blank=True, max_length=2048, null=True),
        ),
        migrations.AlterField(
            model_name='warstats',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
