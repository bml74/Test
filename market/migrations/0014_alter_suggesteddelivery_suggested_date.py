# Generated by Django 4.0.6 on 2023-01-13 23:07

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0013_alter_suggesteddelivery_suggested_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date',
            field=models.DateField(default=datetime.datetime(2023, 1, 13, 23, 7, 45, 692526, tzinfo=utc)),
        ),
    ]
