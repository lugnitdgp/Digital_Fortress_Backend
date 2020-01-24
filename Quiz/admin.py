from django.contrib import admin
# Register your models here.
from .models import Round, Clue, Player, Location, duration
from django.conf import settings


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'lat', 'long',)
    search_fields = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'lat', 'long',)
        }),
    )

    class Media:
        if hasattr(settings, 'GOOGLE_MAPS_API_KEY') and settings.GOOGLE_MAPS_API_KEY:
            css = {
                'all': ('css/admin/location_picker.css',),
            }
            js = (
                'https://maps.googleapis.com/maps/api/js?key={}'.format(
                    settings.GOOGLE_MAPS_API_KEY),
                'js/admin/location_picker.js',
            )


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'score', 'current_hints',
                    'roundNo', 'imageLink', 'submit_time']
    actions = ['clear_all_values']

    def clear_all_values(self, req, queryset):
        queryset.update(score=0)
        queryset.update(roundNo=0)

    clear_all_values.short_description = "Clear all values"


admin.site.register(Clue)
admin.site.register(Round)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(duration)
