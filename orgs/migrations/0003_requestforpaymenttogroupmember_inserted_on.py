# Generated by Django 4.0.6 on 2023-03-20 22:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0002_rename_listing_for_group_members_type_listingforgroupmembers_listing_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestforpaymenttogroupmember',
            name='inserted_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
