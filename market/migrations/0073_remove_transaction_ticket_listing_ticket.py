# Generated by Django 4.0.6 on 2023-03-20 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0072_transaction_ticket'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='ticket',
        ),
        migrations.AddField(
            model_name='listing',
            name='ticket',
            field=models.FileField(blank=True, null=True, upload_to='hoyabay/tickets/digital'),
        ),
    ]
