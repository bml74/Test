# Generated by Django 4.0.6 on 2023-03-23 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0075_transaction_size_alter_paymentintenttracker_listing'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='purchaser_notes',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='seller_notes',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
