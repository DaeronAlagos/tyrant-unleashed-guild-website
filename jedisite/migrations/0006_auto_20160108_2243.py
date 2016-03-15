# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jedisite', '0005_auto_20160107_2136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='decks',
            name='user',
        ),
        migrations.AddField(
            model_name='decks',
            name='account',
            field=models.OneToOneField(null=True, to='jedisite.GameAccount'),
        ),
    ]
