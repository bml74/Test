from django.contrib import admin
from .models import Profile, FollowersCount, ReferralCode #, TwitterHandle


admin.site.register(Profile)
admin.site.register(FollowersCount)
admin.site.register(ReferralCode)
# admin.site.register(TwitterHandle)

