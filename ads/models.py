from django.contrib.auth.models import User, Group
from django.db import models
from django.core.validators import MinValueValidator


class AdOffer(models.Model):
    title = models.CharField(max_length=64, default="Specialization", blank=False, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0, validators=[MinValueValidator(0.0)])
    metric = models.CharField( 
        max_length=32,
        choices=(("Impressions", "Impressions"), ("Unique Impressions", "Unique Impressions"), ("Clicks", "Clicks")),
        default="Impressions",
        blank=False,
    )
    # Add required metric
    # required_impressions
    # required_unique_impressions
    # required_clicks


class AdPurchase(models.Model):
    user_that_purchased_ad = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_that_purchased_ad")
    group_that_purchased_ad = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, related_name="group_that_purchased_ad")
    offer = models.ForeignKey(AdOffer, on_delete=models.CASCADE, null=True, related_name="ad_offer")
    clicks = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    impressions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    unique_impressions = models.ManyToManyField(User, related_name="unique_impressions", default=None, blank=True)

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
