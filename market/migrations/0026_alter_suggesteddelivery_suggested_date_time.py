# Generated by Django 4.0.6 on 2023-01-14 22:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0025_rename_title_lottery_prize_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 14, 22, 37, 27, 842802, tzinfo=utc)),
        ),
    ]
