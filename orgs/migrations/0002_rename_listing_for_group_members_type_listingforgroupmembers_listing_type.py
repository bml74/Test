# Generated by Django 4.0.6 on 2023-01-07 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orgs', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listingforgroupmembers',
            old_name='listing_for_group_members_type',
            new_name='listing_type',
        ),
    ]