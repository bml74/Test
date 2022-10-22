from django.contrib import admin
from .models import Profile, FollowersCount, FollowRequest, ReferralCode #, TwitterHandle


admin.site.register(Profile)
admin.site.register(FollowersCount)
admin.site.register(FollowRequest)
admin.site.register(ReferralCode)
# admin.site.register(TwitterHandle)

