# Generated by Django 4.0.6 on 2023-01-14 00:53

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0017_suggesteddelivery_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='georgetown_location',
            field=models.CharField(blank=True, choices=[('Copley', 'Copley'), ('Darnall', 'Darnall'), ('Harbin', 'Harbin'), ('New South', 'New South'), ('Arrupe', 'Arrupe'), ('Village B', 'Village B'), ('Village A', 'Village A'), ('Henle', 'Henle'), ('LXR', 'Lxr'), ('Kennedy', 'Kennedy'), ('McCarthy', 'Mccarthy'), ('Reynolds', 'Reynolds'), ('Nevils', 'Nevils'), ('Village C', 'Village C'), ('Townhouse', 'Townhouse'), ('Off Campus', 'Off Campus'), ("Leo's", 'Leos'), ('Healy Hall', 'Healy Hall'), ('HSFC', 'Hsfc'), ('Lauinger Library', 'Lau'), ('White-Gravenor', 'White Gravenor'), ('ICC', 'Icc'), ('Leavey Center', 'Leavey Center'), ('Yates', 'Yates'), ('Other', 'Other'), ('None', 'None')], default='None', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 14, 0, 53, 20, 442922, tzinfo=utc)),
        ),
    ]