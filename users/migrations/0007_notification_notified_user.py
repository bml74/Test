# Generated by Django 4.0.6 on 2023-02-24 16:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0006_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notified_user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notified_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
