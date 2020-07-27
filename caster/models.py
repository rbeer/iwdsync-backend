"""caster/model.py
"""
from django.db import models
from django.contrib.auth.models import User


class Caster(models.Model):
    user = models.OneToOneField(
        User, null=True, blank=True, default=None, unique=True, on_delete=models.CASCADE
    )
    twitch_channel = models.CharField(
        max_length=128, default=None, null=True, blank=True, db_index=True, unique=True
    )
    youtube_url = models.CharField(default=None, blank=True, null=True, max_length=1024)
    youtube_time = models.FloatField(default=None, null=True, blank=True)
    irl_time = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return f"Caster - {self.twitch_channel}"
