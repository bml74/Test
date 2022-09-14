from django.db import models


class Map(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField() # Use Quill
    image_url = models.CharField(max_length=512)


class MapGroup(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()


class Marker(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField() # Use Quill
    link = models.CharField(max_length=512)
    color = models.CharField(max_length=16, choices=(
            ("red", "red"),
            ("green", "green"),
            ("blue", "blue")
        )
    )
    # icon = 
    map_group = models.ManyToManyField(MapGroup, blank=True)


