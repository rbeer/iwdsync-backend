from django.contrib import admin
from caster.models import Caster


@admin.register(Caster)
class CasterAdmin(admin.ModelAdmin):
    list_display = ('twitch_channel', )
