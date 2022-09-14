# Generated by Django 4.0.6 on 2022-09-13 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_rename_offer_listing_request_for_help'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='visibility',
            field=models.CharField(choices=[('Invisible', 'Invisible'), ('Private', 'Private'), ('Public', 'Public'), ('Anonymous', 'Anonymous')], default='Private', max_length=100),
        ),
    ]