# Generated by Django 4.0.6 on 2023-01-14 13:58

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0021_alter_suggesteddelivery_suggested_date_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='map_image',
            field=models.FileField(blank=True, null=True, upload_to='listings/images'),
        ),
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 14, 13, 58, 19, 731934, tzinfo=utc)),
        ),
    ]
