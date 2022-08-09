from django.db import models
from django.contrib.auth.models import User
from config.choices import Languages


class Set(models.Model):
    creator = models.ForeignKey(User, related_name='set_creator', on_delete=models.CASCADE)
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=256, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    from_language = models.CharField(max_length=64, choices=Languages.choices, default=Languages.ENGLISH, blank=True)
    to_language = models.CharField(max_length=64, choices=Languages.choices, default=Languages.ENGLISH, blank=True)

    def __str__(self):
        return f"{self.title} by {self.creator.username}" if self.creator else self.title


class Definition(models.Model):
    # language = Languages
    language = models.CharField(
        max_length=64,
        choices=Languages.choices,
        default=Languages.ENGLISH,
        blank=False,
    )
    text = models.CharField(max_length=100)
    definition = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Translation(models.Model):
    from_language = models.CharField(max_length=100)
    to_language = models.CharField(max_length=100)
    text = models.CharField(max_length=100)
    translation = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

class Pair(models.Model):
    from_language = models.CharField(max_length=64, choices=Languages.choices, default=Languages.ENGLISH, blank=False)
    to_language = models.CharField(max_length=64, choices=Languages.choices, default=Languages.ENGLISH, blank=False)
    type = models.CharField(max_length=64, choices=(("Definition", "Definition"), ("Translation", "Translation")), default="Translation", blank=False)
    original_term = models.CharField(max_length=256)
    matching_term = models.CharField(max_length=256)
    set = models.ForeignKey(Set, related_name='set', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)