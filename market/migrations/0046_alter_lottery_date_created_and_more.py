# Generated by Django 4.0.6 on 2023-01-29 17:52

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0045_lottery_date_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lottery',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 29, 17, 52, 33, 637989, tzinfo=utc)),
        ),
    ]
