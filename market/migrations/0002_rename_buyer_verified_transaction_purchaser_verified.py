# Generated by Django 4.0.6 on 2022-09-21 12:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='buyer_verified',
            new_name='purchaser_verified',
        ),
    ]