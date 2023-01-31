# Generated by Django 4.0.6 on 2023-01-29 17:52

import datetime
from django.db import migrations, models
import django.utils.timezone
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0044_alter_suggesteddelivery_suggested_date_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='lottery',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 29, 17, 52, 9, 303217, tzinfo=utc)),
        ),
    ]