# Generated by Django 4.0.6 on 2023-01-07 11:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0004_remove_listing_date_due'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='price',
            field=models.FloatField(default=10, validators=[django.core.validators.MinValueValidator(0.0)]),
        ),
    ]
