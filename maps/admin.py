from django.contrib import admin
from .models import (
    Map, 
    Event,
    EventImage,
    EventVideo
)


admin.site.register(Map)
admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(EventVideo)
