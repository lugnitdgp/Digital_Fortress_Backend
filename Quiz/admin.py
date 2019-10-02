from django.contrib import admin

# Register your models here.
from .models import Round, Clue, Player

admin.site.register(Clue)
admin.site.register(Round)
admin.site.register(Player)
