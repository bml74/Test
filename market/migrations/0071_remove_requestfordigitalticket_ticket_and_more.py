# Generated by Django 4.0.6 on 2023-03-20 22:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('market', '0070_remove_listing_ticket_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestfordigitalticket',
            name='ticket',
        ),
        migrations.AddField(
            model_name='requestfordigitalticket',
            name='user_receiving_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_receiving_request_and_thus_sending_ticket', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='requestfordigitalticket',
            name='user_sending_request',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_sending_request_and_thus_receiving_ticket', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='TicketFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket', models.FileField(blank=True, null=True, upload_to='hoyabay/tickets/digital')),
                ('inserted_on', models.DateTimeField(auto_now_add=True)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.transaction')),
            ],
        ),
    ]
