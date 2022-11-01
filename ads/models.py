from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from ecoles.models import Specialization, Course
from posts.models import Post
from market.models import Listing


class AdOffer(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, )
    title = models.CharField(max_length=64, default="Ad Offer", blank=False, unique=True)
    description = models.TextField(blank=False, default="Description for ad offer")
    price = models.FloatField(default=0, validators=[MinValueValidator(0.0)])
    metric = models.CharField( 
        max_length=32,
        choices=(("Impressions", "Impressions"), ("Unique Impressions", "Unique Impressions"), ("Clicks", "Clicks")),
        default="Impressions",
        blank=False,
    )
    # Add required metric
    required_impressions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    required_unique_impressions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    required_clicks = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    def get_metric(self):
        return self.metric

    def get_price(self):
        return self.price

    def get_required_metric(self):
        if self.get_metric() == "Impressions":
            return self.required_impressions
        elif self.get_metric() == "Unique Impressions":
            return self.required_unique_impressions
        elif self.get_metric() == "Clicks":
            return self.required_clicks

    def get_price_per_required_metric(self):
        try:
            if self.get_metric() == "Impressions":
                return self.get_price() / self.required_impressions
            elif self.get_metric() == "Unique Impressions":
                return self.get_price() / self.required_unique_impressions
            elif self.get_metric() == "Clicks":
                return self.get_price() / self.required_clicks
        except ZeroDivisionError:
            return 0

    def __str__(self):
        return f"{self.title} (Total Price: ${self.price})"

    def get_absolute_url(self):
        return reverse('ad-offer', kwargs={'pk': self.pk})


class AdPurchase(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, )
    user_that_purchased_ad = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_that_purchased_ad")
    group_that_purchased_ad = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True, related_name="group_that_purchased_ad")
    offer = models.ForeignKey(AdOffer, on_delete=models.CASCADE, null=True, related_name="ad_offer")
    clicks = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    impressions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    unique_impressions = models.ManyToManyField(User, related_name="unique_impressions", default=None, blank=True)
    ad_type = models.CharField( 
        max_length=32,
        choices=(
            ("Specialization", "Specialization"), 
            ("Course", "Course"), 
            ("Post", "Post"),
            ("Listing", "Listing"),
            ("General Advertisement", "General Advertisement"),
        ),
        default="General Advertisement",
    )
    specialization_to_be_advertised = models.ForeignKey(Specialization, on_delete=models.CASCADE, blank=True, null=True, related_name="specialization_to_be_advertised")
    course_to_be_advertised = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True, related_name="course_to_be_advertised")
    listing_to_be_advertised = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listing_to_be_advertised")
    post_to_be_advertised = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True, related_name="post_to_be_advertised")    
    general_advertisement_text = models.CharField(max_length=128, blank=True, null=True)

    def get_metric(self):
        return self.offer.metric

    def get_price(self):
        return self.offer.price

    def get_current_price_per_metric(self):
        if self.get_metric() == "Impressions":
            return self.get_price() / self.impressions
        elif self.get_metric() == "Unique Impressions":
            return self.get_price() / self.unique_impressions.count
        elif self.get_metric() == "Clicks":
            return self.get_price() / self.clicks

    def get_absolute_url(self):
        return reverse('ad-purchase', kwargs={'pk': self.pk})
