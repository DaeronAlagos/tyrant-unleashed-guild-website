from django.contrib import admin
from jedisite.models import GameAccount, Decks, TyrantSettings, Benchmarks, ActionLog, WarStats


# Add search box to admin decks page
class DecksAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'mode', 'friendly_structures', 'enemy_structures')
    search_fields = ('name',)


# Change admin war stats page display fields
class WarStatsAdmin(admin.ModelAdmin):
    list_display = ('name', 'friendly_guild', 'enemy_guild')


# Models registered to display in admin
admin.site.register(GameAccount)
admin.site.register(Decks, DecksAdmin)
admin.site.register(TyrantSettings)
admin.site.register(Benchmarks)
admin.site.register(ActionLog)
admin.site.register(WarStats, WarStatsAdmin)
