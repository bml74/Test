# Generated by Django 4.0.6 on 2023-02-24 17:00

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0056_alter_suggesteddelivery_suggested_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 24, 17, 0, 28, 262051, tzinfo=utc)),
        ),
    ]
