from django.db import models
from django.contrib.auth.models import User, Group
from django_countries.fields import CountryField



class TwitterHandle(models.Model):
    twitter_handle = models.CharField(max_length=256, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_twitter_handle")

    def __str__(self):
        return f"Twitter handle: @{self.twitter_handle}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField(default=0, null=False)
    verified_course_creator = models.BooleanField(default=False)
    select_view_seen = models.BooleanField(default=False, null=False, blank=False) # Has user seen select view?
    primary_twitter_handle = models.ForeignKey(TwitterHandle, on_delete=models.CASCADE, blank=True, null=True)
    country = CountryField(default='US')

    def __str__(self):
        return f'{self.user.username} Profile'


class ReferralCode(models.Model):
    referral_code = models.CharField(max_length=16, blank=True, null=True, unique=True)
    generatedBy = models.OneToOneField(User, on_delete=models.CASCADE, related_name="generatedBy")
    usedBy = models.ManyToManyField(
        User,
        related_name="usedBy",
        default=None,
        blank=True
    )


class FollowersCount(models.Model):
    follower_of_user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="follower_of_user")
    user_being_followed = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_being_followed")

    def __str__(self):
        return f"{self.user_being_followed.username} followed by {self.follower_of_user.username}"


