from django.db import models
from django.contrib.auth.models import User, Group


class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    group_visibility = models.CharField(
        max_length=64,
        choices=(("Private", "Private"), ("Public", "Public")),
        default="Private",
        blank=False,
    )
    group_type = models.CharField(
        max_length=64,
        choices=(
            ("Group", "Group"), 
            ("Club", "Club"), 
            ("Business", "Business"), 
            ("Nonprofit", "Nonprofit"), 
            ("Graduate School", "Graduate School"), 
            ("University", "University"), 
            ("High School", "High School"),
            ("Middle School", "Middle School"),
            ("Elementary School", "Elementary School"),
            ("Other", "Other")
        ),
        default="Group",
        blank=False,
    )
    # group_industry = models.CharField(
    #     max_length=64,
    #     choices=(("Software", "Software"), ("Manufacturing", "Manufacturing"), ("Pharmaceuticals", "Pharmaceuticals")),
    #     blank=True,
    # )
    group_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="group_creator")
    group_members = models.ManyToManyField(
        User,
        related_name="group_members",
        default=None,
        blank=True
    )
    group_followers = models.ManyToManyField(
        User,
        related_name="group_followers",
        default=None,
        blank=True
    )

    def __str__(self):
        return f'{self.group.name} Profile'


class GroupFollowRequest(models.Model):
    date_time_requested = models.DateTimeField(auto_now_add=True) 
    user_requesting_to_follow_group = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_requesting_to_follow_group") 
    group_receiving_follow_request = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_receiving_follow_request") 


class GroupMembershipRequest(models.Model):
    date_time_requested = models.DateTimeField(auto_now_add=True) 
    user_requesting_to_become_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_requesting_to_become_member") 
    group_receiving_membership_request = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_receiving_membership_request") 
