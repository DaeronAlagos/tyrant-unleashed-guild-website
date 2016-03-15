# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jedisite', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Decks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cards', models.CharField(max_length=256)),
                ('mode', models.CharField(max_length=30)),
                ('type', models.CharField(max_length=30)),
                ('structures', models.CharField(max_length=60)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='gameaccount',
            name='canvas',
            field=models.URLField(unique=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='gameaccount',
            name='guild',
            field=models.CharField(max_length=128),
        ),
        migrations.DeleteModel(
            name='Guilds',
        ),
    ]
