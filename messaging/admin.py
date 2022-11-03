from django.contrib import admin
from .models import DirectMessage, Room, RoomMembershipRequest


admin.site.register(DirectMessage)
admin.site.register(Room)
admin.site.register(RoomMembershipRequest)