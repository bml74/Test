# Generated by Django 4.0.6 on 2023-03-21 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0073_remove_transaction_ticket_listing_ticket'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ticketfile',
            old_name='ticket',
            new_name='ticket_file',
        ),
    ]