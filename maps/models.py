from django.db import models
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from django.urls import reverse


class AlternativeCityNames(TaggedItemBase):
    content_object = models.ForeignKey('Event', on_delete=models.CASCADE)
    

class AlternativeRegionNames(TaggedItemBase):
    content_object = models.ForeignKey('Event', on_delete=models.CASCADE)


class AlternativeCountryNames(TaggedItemBase):
    content_object = models.ForeignKey('Event', on_delete=models.CASCADE)


class Map(models.Model): 
    title = models.CharField(max_length=64)
    description = models.TextField() # Use Quill
    image_url = models.CharField(max_length=512)
    excel_upload = models.FileField(upload_to='map_excel_files', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('map', kwargs={'pk': self.pk})



class Event(models.Model):
    # address, postcode, district, neighborhood
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField(blank=True, null=True)
    geometry = models.CharField(default="Point", max_length=16)
    # details_available = models.BooleanField(default=False)
    """
    day = models.CharField(max_length=12, choices=(
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
            ("Sunday", "Sunday")
        )
    )
    """
    primary_city_name = models.CharField(max_length=64, blank=True, null=True)
    alternative_city_names = TaggableManager(through=AlternativeCityNames, related_name='alternative_city_names', verbose_name='Alternative city names')

    primary_region_name = models.CharField(max_length=64, blank=True, null=True)
    alternative_region_names = TaggableManager(through=AlternativeRegionNames, related_name='alternative_region_names', verbose_name='Alternative region names')

    primary_country_name = models.CharField(max_length=64, blank=True, null=True)
    alternative_country_names = TaggableManager(through=AlternativeCountryNames, related_name='alternative_country_names', verbose_name='Alternative country names')

    address = models.CharField(max_length=256, blank=True, null=True)
    postcode = models.CharField(max_length=256, blank=True, null=True)
    district = models.CharField(max_length=256, blank=True, null=True)
    neighborhood = models.CharField(max_length=256, blank=True, null=True)

    anchor_date = models.DateField(default='1945-09-01')
    number_of_days_after_anchor_date_that_event_began = models.IntegerField(default=0)
    number_of_days_after_anchor_date_that_event_started = models.IntegerField(default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    title = models.CharField(max_length=64, default="Title")
    description = models.TextField(default="Description") # Use Quill
    link = models.CharField(max_length=512, blank=True, null=True)
    color = models.CharField(max_length=16, blank=True, null=True, choices=(
            ("red", "red"),
            ("green", "green"),
            ("blue", "blue")
        )
    )
    # Others to add for Yahad: Type of place before; Num. Memorials; Occupation_period
    # user
    # group


class EventDetails(models.Model):
    description = models.TextField(blank=True, null=True)
    number_of_sub_sites = models.IntegerField(default=1, blank=True, null=True)
    number_of_casualties = models.IntegerField(default=1, blank=True, null=True)
