# Generated by Django 4.0.6 on 2023-01-30 03:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0002_adpurchase_listing_to_be_advertised'),
    ]

    operations = [
        migrations.AddField(
            model_name='adpurchase',
            name='num_unique_impressions',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
