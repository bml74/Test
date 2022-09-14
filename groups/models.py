from django.db import models
from django.contrib.auth.models import User, Group
from users.models import TwitterHandle


class GroupProfile(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    group_visibility = models.CharField(
        max_length=64,
        choices=(("Invisible", "Invisible"), ("Private", "Private"), ("Public", "Public")),
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
    # primary_twitter_handle = models.ForeignKey('users.TwitterHandle', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.group.name} Profile'


class GroupFollowersCount(models.Model):
    follower_of_group = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="follower_of_group")
    group_being_followed = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, related_name="group_being_followed")

    def __str__(self):
        return f'Group "{self.group_being_followed.name}" followed by {self.follower_of_group.username}'