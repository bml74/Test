from django.db import models


class MapMeta(models.Model):
    title = models.CharField(max_length=64)
    keyword = models.CharField(max_length=256)

    def __str__(self):
        return self.title
