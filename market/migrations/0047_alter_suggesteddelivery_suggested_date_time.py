# Generated by Django 4.0.6 on 2023-01-30 03:21

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0046_alter_lottery_date_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 30, 3, 21, 23, 22740, tzinfo=utc)),
        ),
    ]
