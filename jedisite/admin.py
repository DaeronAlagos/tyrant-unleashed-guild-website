from django.contrib import admin
from jedisite.models import GameAccount, Decks, TyrantSettings, Benchmarks, ActionLog, WarStats

# Register your models here.
admin.site.register(GameAccount)
admin.site.register(Decks)
admin.site.register(TyrantSettings)
admin.site.register(Benchmarks)
admin.site.register(ActionLog)
admin.site.register(WarStats)
