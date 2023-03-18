import random
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator
from ecoles.choices import Visibility
from config.choices import DeliveryLocations
from django.conf import settings
from .utils import listing_category_options_list_of_tups
from orgs.models import ListingForGroupMembers


class Listing(models.Model):
    title = models.CharField(max_length=128, default="Listing", blank=False)
    image = models.FileField(upload_to='listings/images', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(default=50, validators=[MinValueValidator(1)])
    date_listed = models.DateTimeField(auto_now_add=True)
    # listing_ends_on = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="user_that_created_listing")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True, related_name="group_that_created_listing")
    visibility = models.CharField(
        max_length=100,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        blank=False,
        null=False
    )
    listing_type = models.CharField(
        max_length=100,
        choices=(("Offer (Looking to sell)", "Offer (Looking to sell)"), ("Bid (Looking to buy)", "Bid (Looking to buy)")),
        default="Offer (Looking to sell)",
    )
    listing_category = models.CharField(
        max_length=100,
        choices=listing_category_options_list_of_tups,
        default="Book",
    )
    condition = models.CharField(
        max_length=100,
        choices=(
            ("Brand new (5/5)", "Brand new (5/5)"), 
            ("Very good condition (4/5)", "Very good condition (4/5)"),
            ("Used but in good condition (3/5)", "Used but in good condition (3/5)"), 
            ("Used and in ok condition (2/5)", "Used and in ok condition (2/5)"),
            ("Poor condition (1/5)", "Poor condition (1/5)"),
        ),
        blank=True,
        null=True,
    )
    listing_medium = models.CharField(
        max_length=100,
        choices=(("Digital File(s)", "Digital File(s)"), ("In-Person Service", "In-Person Service"), ("Digital Service", "Digital Service"), ("Physical Product", "Physical Product")),
        default="Physical Product",
    )  
    infinite_copies_available = models.BooleanField(default=False, blank=False, null=False) # If non-fungible, then unique and one-time purchase.
    quantity_available = models.IntegerField(default=1, blank=True, null=True, validators=[MinValueValidator(0.00)])
    quantity_sold = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0.00)])
    purchasers = models.ManyToManyField(User, related_name="purchasers", default=None, blank=True)
    # condition
    # size

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('listing', kwargs={'pk': self.pk})


class SuggestedDelivery(models.Model):
    deliveryLocation = models.CharField(
        max_length=100,
        choices=DeliveryLocations.choices,
        default=DeliveryLocations.NONE,
        blank=True,
        null=True
    )
    suggested_date_time = models.DateTimeField(auto_now_add=False, default=timezone.now())
    listing = models.ForeignKey(Listing, null=True, blank=True, related_name="seller", on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="seller_of_listing")
    purchaser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="purchaser_of_listing")
    seller_verified = models.BooleanField(null=True, blank=True)
    purchaser_verified = models.BooleanField(null=True, blank=True)
    transaction_id = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.CharField(
        max_length=100,
        choices=(("Seller", "Seller"), ("Buyer", "Buyer")),
        default="Seller",
    )  

    def __str__(self):
        return f"Suggested delivery #{self.id} by {self.created_by} for Transaction (ID: {self.transaction_id})"

    def get_absolute_url(self):
        return reverse('transaction-delivery', kwargs={'transaction_pk': self.transaction_id})


class Lottery(models.Model):
    prize = models.CharField(max_length=128, default="Lottery Prize")
    image = models.FileField(upload_to='lotteries/images', blank=True, null=True)
    num_unique_users = models.IntegerField(default=0)
    num_unique_users_required = models.IntegerField(default=500)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="lottery_winner")
    date_created = models.DateTimeField(auto_now_add=True)

    def select_lucky_number(self):
        if not self.winner:
            if self.num_unique_users >= self.num_unique_users_required:
                return random.randrange(self.num_unique_users)
        return False

    def __str__(self):
        return self.prize

    def get_absolute_url(self):
        return reverse('lottery', kwargs={'pk': self.pk}) 


class LotteryParticipant(models.Model):
    lottery_participant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="lottery_participant")
    fk_lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, null=True, related_name="fk_lottery")

    def get_absolute_url(self):
        return reverse('lottery', kwargs={'pk': self.fk_lottery.id}) 

    def __str__(self):
        return f""

"""
from market.models import Lottery, LotteryParticipant
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
lottery = get_object_or_404(Lottery, id=1)
participants = list(LotteryParticipant.objects.filter(fk_lottery=lottery))
num = lottery.select_lucky_number()
print(num)
"""


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
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="seller")
    purchaser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="purchaser")
    seller_verified = models.BooleanField(null=True, blank=True)
    purchaser_verified = models.BooleanField(null=True, blank=True)
    transaction_id = models.CharField(max_length=128, null=True, blank=True, unique=True)
    value = models.FloatField(default=0)
    description = models.CharField(max_length=256,null=True, blank=True)
    inserted_on = models.DateTimeField(auto_now_add=True)
    end_payment_sent = models.BooleanField(default=False)

    delivery = models.ForeignKey(SuggestedDelivery, on_delete=models.CASCADE, null=True, blank=True, related_name="delivery")

    def __str__(self):
        return f"Transaction #{self.transaction_id}"

    def get_absolute_url(self):
        return reverse('transaction', kwargs={'pk': self.pk})


class PaymentIntentTracker(models.Model):
    stripe_payment_intent_id = models.CharField(max_length=264, null=False, blank=False, unique=True)
    stripe_account_id = models.CharField(max_length=264, null=False, blank=False, unique=False)
    listing = models.ForeignKey(Listing, null=True, blank=True, unique=False, on_delete=models.PROTECT)
    listing_for_group_members = models.ForeignKey(ListingForGroupMembers, null=True, blank=True, unique=False, on_delete=models.PROTECT)
    user = models.ForeignKey(User, blank=False, null=False, unique=False, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['stripe_account_id', 'listing', 'user'], name='unique_payment_intent')
        ]