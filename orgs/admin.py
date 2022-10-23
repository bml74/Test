from django.contrib import admin
from .models import GroupProfile, GroupFollowRequest, GroupMembershipRequest


admin.site.register(GroupProfile)
admin.site.register(GroupFollowRequest)
admin.site.register(GroupMembershipRequest)

