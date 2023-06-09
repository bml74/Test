# Generated by Django 4.0.6 on 2023-03-23 17:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0074_rename_ticket_ticketfile_ticket_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='size',
            field=models.CharField(blank=True, choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL')], max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='paymentintenttracker',
            name='listing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='market.listing'),
        ),
    ]
