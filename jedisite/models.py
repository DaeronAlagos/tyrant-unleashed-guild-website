from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import User


# Create your models here.


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    line_name = models.CharField(max_length=64, blank=True)

    def __unicode__(self):
        return self.user.username


class GameAccount(models.Model):
    user = models.ForeignKey(User)

    kong_name = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=64, unique=True)
    canvas = models.URLField(max_length=1024)
    postdata = models.CharField(max_length=1024)
    guild = models.CharField(max_length=128)
    inventory = JSONField(null=True)
    allow_command = models.BooleanField(default=False)
    show_canvas = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Decks(models.Model):

    name = models.CharField(max_length=30)
    guild = models.CharField(max_length=30, blank=True)
    deck = JSONField()
    mode = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
    bge = JSONField()
    friendly_structures = models.CharField(max_length=128)
    enemy_structures = models.CharField(max_length=128)
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Benchmarks(models.Model):

    deck = models.ForeignKey(Decks)
    score = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.deck.name


class ActionLog(models.Model):

    user = models.ForeignKey(User)
    event = models.CharField(max_length=128)
    target = models.ForeignKey(GameAccount)
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username


class WarStats(models.Model):

    name = models.CharField(max_length=64)
    enemy = models.CharField(max_length=64)
    data = JSONField()
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class TyrantSettings(models.Model):

    name = models.CharField(max_length=30)
    value = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name
