from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
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
    postdata = models.CharField(max_length=2048, blank=True, null=True)
    guild = models.CharField(max_length=128)
    inventory = ArrayField(
        models.CharField(max_length=64, blank=True),
        blank=True,
        null=True,
    )
    allow_command = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class Decks(models.Model):

    name = models.CharField(max_length=30)
    guild = models.CharField(max_length=30, blank=True)
    deck = JSONField()
    mode = models.CharField(max_length=30)
    type = models.CharField(max_length=30)
    bge = JSONField()
    friendly_structures = models.CharField(max_length=128, blank=True)
    enemy_structures = models.CharField(max_length=128, blank=True)
    date = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Benchmarks(models.Model):

    deck = models.ForeignKey(Decks)
    score = models.DecimalField(max_digits=6, decimal_places=3)
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
    friendly_guild = models.CharField(max_length=64)
    enemy_guild = models.CharField(max_length=64)
    data = JSONField()
    date = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __unicode__(self):
        return self.name


class TyrantSettings(models.Model):

    name = models.CharField(max_length=30)
    value = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name
