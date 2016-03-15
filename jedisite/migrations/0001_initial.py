# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('canvas', models.CharField(unique=True, max_length=256)),
                ('postdata', models.URLField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Guilds',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
            ],
        ),
        migrations.AddField(
            model_name='gameaccount',
            name='guild',
            field=models.OneToOneField(to='jedisite.Guilds'),
        ),
        migrations.AddField(
            model_name='gameaccount',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
