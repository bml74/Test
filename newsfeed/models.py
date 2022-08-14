from django.urls import reverse
from django.db import models
from news.models import Source
from django.contrib.auth.models import User

# Create your models here.
class Feed(models.Model):

    title = models.CharField(max_length=64, default="Feed", blank=False)
    url = models.CharField(max_length=1024, default="", blank=False)
    category = models.CharField(max_length=64, blank=True)

    source = models.ForeignKey(Source, on_delete=models.CASCADE, null=True, related_name="feed_source")

    followers = models.ManyToManyField( 
        User,
        related_name="feed_followers",
        default=None,
        blank=True 
    )

    def __str__(self):
        return f"{self.title} | {self.source.source_name}"

    def get_absolute_url(self):
        return reverse('feed-detail', kwargs={'pk': self.pk})
