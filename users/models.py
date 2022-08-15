from django.db import models
from django.contrib.auth.models import User, Group


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    # country = models.CharField(CHOICES)

    def __str__(self):
        return f'{self.user.username} Profile'