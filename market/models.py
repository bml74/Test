from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator

from ecoles.choices import Visibility


class Listing(models.Model):
    title = models.CharField(max_length=64, default="Listing", blank=False)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=0, validators=[MinValueValidator(0.0)])
    date_listed = models.DateTimeField(auto_now_add=True)
    date_due = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_that_created_listing")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="group_that_created_listing")
    visibility = models.CharField(
        max_length=100,
        choices=Visibility.choices,
        default=Visibility.ANONYMOUS,
        blank=False,
        null=False
    )
    listing_type = models.CharField(
        max_length=100,
        choices=(("Offer", "Offer"), ("Request", "Request")),
        default="Request",
    )
    listing_category = models.CharField(
        max_length=100,
        choices=(("General", "General"), ("Homework", "Homework"), ("Consulting", "Consulting"), ("Tutoring", "Tutoring"), ("Sale", "Sale")),
        default="General",
    )
    listing_medium = models.CharField(
        max_length=100,
        choices=(("Digital File(s)", "Digital File(s)"), ("In-Person Service", "In-Person Service"), ("Digital Service", "Digital Service"), ("Physical Product", "Physical Product")),
        default="General",
    )  
    infinite_copies_available = models.BooleanField(default=True, blank=False, null=False) # If non-fungible, then unique and one-time purchase.
    quantity_available = models.IntegerField(default=1, blank=True, null=True)
    quantity_sold = models.IntegerField(default=0, blank=True, null=True)
    purchasers = models.ManyToManyField(User, related_name="purchasers", default=None, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listing', kwargs={'pk': self.pk})


class Fundraiser(models.Model):
    title = models.CharField(max_length=64, default="Fundraiser", blank=False)
    description = models.TextField()
    price = models.IntegerField(default=25)
    funds_needed = models.IntegerField(default=25)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_that_created_fundraiser")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="group_that_created_fundraiser")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('fundraiser_detail_view', kwargs={'pk': self.pk})


class Transaction(models.Model):
    transaction_obj_type = models.CharField(max_length=128)
    transaction_obj_id = models.IntegerField(default=0)
    title = models.CharField(max_length=128, default="")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="seller")
    purchaser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="purchaser")
    seller_verified = models.BooleanField(null=True, blank=True)
    purchaser_verified = models.BooleanField(null=True, blank=True)
    transaction_id = models.CharField(max_length=128, null=True, blank=True)
    value = models.FloatField(default=0)
    description = models.CharField(max_length=256,null=True, blank=True)
    inserted_on = models.DateTimeField(auto_now_add=True)
    end_payment_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction #{self.transaction_id}"

    def get_absolute_url(self):
        return reverse('transaction', kwargs={'pk': self.pk})

