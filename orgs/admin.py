from django.contrib import admin
from .models import GroupProfile, GroupFollowRequest, GroupMembershipRequest, ListingForGroupMembers, RequestForPaymentToGroupMember


admin.site.register(GroupProfile)
admin.site.register(GroupFollowRequest)
admin.site.register(GroupMembershipRequest)
admin.site.register(ListingForGroupMembers)
admin.site.register(RequestForPaymentToGroupMember)

