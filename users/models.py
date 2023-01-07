from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User, Group
from django_countries.fields import CountryField
from django.conf import settings


class TwitterHandle(models.Model):
    twitter_handle = models.CharField(max_length=256, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_twitter_handle")

    def __str__(self):
        return f"Twitter handle: @{self.twitter_handle}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField(default=0, null=False)
    verified_creator = models.BooleanField(default=False)
    has_super_status = models.BooleanField(default=False)
    primary_twitter_handle = models.ForeignKey(TwitterHandle, on_delete=models.CASCADE, blank=True, null=True)
    country = CountryField(default='US')
    hasUsedAReferralCode = models.BooleanField(default=False)
    visibility = models.CharField( 
        max_length=8,
        choices=(("Public", "Public"), ("Private", "Private")),
        default="Public",
        blank=False,
    )
    ACCOUNT_BALANCE = models.FloatField(default=0.0)
    venmoHandle = models.CharField(max_length=256, blank=True, null=True)

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


class FollowRequest(models.Model):
    date_time_requested = models.DateTimeField(auto_now_add=True) 
    user_requesting_to_follow = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_requesting_to_follow") 
    user_receiving_follow_request = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_receiving_follow_request") 



