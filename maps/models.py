from django.db import models
from taggit.models import TaggedItemBase
from django.urls import reverse
from django.contrib.auth.models import User


class Map(models.Model): 
    title = models.CharField(max_length=64, default="Title", unique=True)
    description = models.TextField(default="Description") 
    map_image = models.FileField(upload_to='map_images', blank=True, null=True)
    anchor_date = models.DateField(default='1939-09-01')
    last_date = models.DateField(default='1945-05-01')
    excel_upload = models.FileField(upload_to='map_excel_files', blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('map', kwargs={'pk': self.pk})



class Event(models.Model):
    parent_map = models.ForeignKey(Map, on_delete=models.CASCADE, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(blank=True, null=True)
    geometry = models.CharField(default="Point", max_length=16)
    alternative_id = models.IntegerField(blank=True, null=True)
    content_online = models.BooleanField(default=False)
    dates = models.CharField(max_length=256, blank=True, null=True)
    hours = models.CharField(max_length=256, blank=True, null=True)
    day = models.CharField(max_length=12, blank=True, null=True, choices=(
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday")
        )
    )
    primary_city_name = models.CharField(max_length=64, blank=True, null=True)
    alternative_city_names = models.CharField(max_length=256, blank=True, null=True, verbose_name='Alternative city names')
    # alternative_city_names = TaggableManager(through=AlternativeCityNames, related_name='alternative_city_names', verbose_name='Alternative city names', blank=True)

    primary_region_name = models.CharField(max_length=64, blank=True, null=True)
    alternative_region_names = models.CharField(max_length=256, blank=True, null=True, verbose_name='Alternative region names')
    # alternative_region_names = TaggableManager(through=AlternativeRegionNames, related_name='alternative_region_names', verbose_name='Alternative region names', blank=True)

    primary_country_name = models.CharField(max_length=64, blank=True, null=True, default="Ukraine")
    alternative_country_names = models.CharField(max_length=256, blank=True, null=True, verbose_name='Alternative country names')
    # alternative_country_names = TaggableManager(through=AlternativeCountryNames, related_name='alternative_country_names', verbose_name='Alternative country names', blank=True)

    address = models.CharField(max_length=256, blank=True, null=True)
    postcode = models.CharField(max_length=256, blank=True, null=True)
    district = models.CharField(max_length=256, blank=True, null=True)
    neighborhood = models.CharField(max_length=256, blank=True, null=True)

    number_of_days_after_anchor_date_that_event_began = models.IntegerField(default=0, blank=True, null=True)
    number_of_days_after_anchor_date_that_event_ended = models.IntegerField(default=0, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    title = models.CharField(max_length=64, default="Title", blank=True, null=True)
    description = models.TextField(default="Description", blank=True, null=True) # Use Quill
    link = models.CharField(max_length=512, blank=True, null=True)
    marker_color = models.CharField(max_length=16, blank=True, null=True, choices=(
            ("red", "red"),
            ("green", "green"),
            ("blue", "blue")
        )
    )
    number_of_sites = models.IntegerField(default=1, blank=True, null=True)
    number_of_casualties = models.CharField(max_length=128, default="0", blank=True, null=True)
    number_of_memorials = models.IntegerField(blank=True, null=True)
    type_of_place_before_event = models.CharField(max_length=128, default="", blank=True, null=True)
    occupation_period = models.CharField(max_length=256, blank=True, null=True)
    map_event_followers = models.ManyToManyField(
        User, 
        related_name="map_event_followers", 
        default=None, 
        blank=True
    )

    def __str__(self):
        return self.primary_city_name

    def get_absolute_url(self):
        return reverse('event', kwargs={'pk': self.pk})


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('event', kwargs={'pk': self.event.pk})


class EventVideo(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    link = models.URLField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('event', kwargs={'pk': self.event.pk})

