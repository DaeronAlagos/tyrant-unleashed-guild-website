from __future__ import unicode_literals

import os
from django.db import models
from django.conf import settings


class ConquestZones(models.Model):

    name = models.CharField(max_length=32)
    path = os.path.join(settings.STATIC_PATH, '/images/conquest')
    image = models.FilePathField(path=path)
    bge = models.CharField(max_length=32, blank=True)
    tier = models.IntegerField()

    def __unicode__(self):
        return self.name
