# Generated by Django 4.0.6 on 2023-01-28 17:43

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0033_alter_suggesteddelivery_suggested_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 28, 17, 43, 19, 775552, tzinfo=utc)),
        ),
    ]
