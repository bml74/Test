# Generated by Django 4.0.6 on 2022-10-24 17:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0004_alter_adoffer_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='adoffer',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='adpurchase',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
