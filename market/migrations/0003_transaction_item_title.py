# Generated by Django 4.0.6 on 2022-09-21 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_rename_buyer_verified_transaction_purchaser_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='item_title',
            field=models.CharField(default='', max_length=128),
        ),
    ]