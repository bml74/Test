from django.contrib import admin
from .models import Map, MapGroup, Marker, Event


admin.site.register(Map)
admin.site.register(MapGroup)
admin.site.register(Marker)
admin.site.register(Event)
