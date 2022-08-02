from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Entity(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    date_entered = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['-date_entered']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('entity-detail', kwargs={'pk': self.pk})


class Chain(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    date_entered = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('chain-detail', kwargs={'pk': self.pk})


class Era(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    date_entered = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('era-detail', kwargs={'pk': self.pk})


class Theme(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    date_entered = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('theme-detail', kwargs={'pk': self.pk})


class TwoSidedFinancialTransaction(models.Model):
    
    entity_1 = models.CharField(max_length=256)
    type_of_asset_received_by_entity_1 = models.CharField(
        max_length=64, 
        choices=(
            ("Cash", "Cash"),
            ("Credit", "Credit"),
            ("Real Estate", "Real Estate"),
            ("Stock", "Stock"),
            ("Bond", "Bond"),
            ("Physical Asset", "Physical Asset"),
            ("Painting", "Painting"),
        ),
        default="Cash",
        blank=True,
        null=True
    )
    description_of_asset_received_by_entity_1 = models.CharField(max_length=256)
    monetary_value_of_asset_received_by_entity_1 = models.FloatField(default=0.0)
    monetary_value_of_asset_received_by_entity_1_is_estimated = models.BooleanField(default=False)
    currency_of_asset_received_by_entity_1_if_applicable = models.CharField(
        max_length=8, 
        choices=(
            ("USD", "USD"),
            ("RUB", "RUB"),
            ("EUR", "EUR"),
            ("AUD", "AUD"),
            ("CAD", "CAD"),
            ("CNY", "CNY"),
            ("JPY", "JPY")
        ),
        default=None,
        blank=True,
        null=True
    )

    entity_2 = models.CharField(max_length=256)
    type_of_asset_received_by_entity_2 = models.CharField(
        max_length=64, 
        choices=(
            ("Cash", "Cash"),
            ("Credit", "Credit"),
            ("Real Estate", "Real Estate"),
            ("Stock", "Stock"),
            ("Bond", "Bond"),
            ("Physical Asset", "Physical Asset"),
            ("Painting", "Painting"),
        ),
        default="Cash",
        blank=True,
        null=True
    )
    description_of_asset_received_by_entity_2 = models.CharField(max_length=256)
    monetary_value_of_asset_received_by_entity_2 = models.FloatField(default=0.0)
    monetary_value_of_asset_received_by_entity_2_is_estimated = models.BooleanField(default=False)
    currency_of_asset_received_by_entity_2_if_applicable = models.CharField(
        max_length=8, 
        choices=(
            ("USD", "USD"),
            ("RUB", "RUB"),
            ("EUR", "EUR"),
            ("AUD", "AUD"),
            ("CAD", "CAD"),
            ("CNY", "CNY"),
            ("JPY", "JPY")
        ),
        default="USD",
        blank=True,
        null=True
    )

    crime = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    date_entered = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    citation = models.TextField(blank=True, null=True)
    entities = models.ManyToManyField(Entity, related_name="transaction_entities", default=None, blank=True)
    chains = models.ManyToManyField(Chain, related_name="transaction_chains", default=None, blank=True)
    eras = models.ManyToManyField(Era, related_name="transaction_eras", default=None, blank=True)
    themes = models.ManyToManyField(Theme, related_name="transaction_themes", default=None, blank=True)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('transaction-detail', kwargs={'pk': self.pk})
