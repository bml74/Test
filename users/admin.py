from django.contrib import admin
from .models import Profile, FollowersCount #, TwitterHandle


admin.site.register(Profile)
admin.site.register(FollowersCount)
# admin.site.register(TwitterHandle)

