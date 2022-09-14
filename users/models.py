from django.db import models
from django.contrib.auth.models import User, Group


class TwitterHandle(models.Model):
    twitter_handle = models.CharField(max_length=256, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_twitter_handle")

    def __str__(self):
        return f"Twitter handle: @{self.twitter_handle}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    num_credits = models.IntegerField(default=0, null=False)
    verified_course_creator = models.BooleanField(default=False)
    select_view_seen = models.BooleanField(default=False, null=False, blank=False) # Has user seen select view?
    # primary_twitter_handle = models.ForeignKey('users.TwitterHandle', on_delete=models.CASCADE, blank=True, null=True)
    # country = models.CharField(CHOICES)

    def __str__(self):
        return f'{self.user.username} Profile'


class FollowersCount(models.Model):
    follower_of_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="follower_of_user")
    user_being_followed = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_being_followed")

    def __str__(self):
        return f"{self.user_being_followed.username} followed by {self.follower_of_user.username}"


