# Generated by Django 4.0.6 on 2023-02-22 19:11

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0053_alter_listing_listing_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 22, 19, 11, 34, 424227, tzinfo=utc)),
        ),
    ]
