# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-16 19:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0022_decks_cq_zone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='decks',
            name='bge',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='decks',
            name='cq_zone',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='decks',
            name='enemy_structures',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='decks',
            name='friendly_structures',
            field=models.CharField(max_length=60, null=True),
        ),
    ]