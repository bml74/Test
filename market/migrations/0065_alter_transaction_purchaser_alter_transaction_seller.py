# Generated by Django 4.0.6 on 2023-03-19 22:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('market', '0064_alter_suggesteddelivery_suggested_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='purchaser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='purchaser', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='seller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='seller', to=settings.AUTH_USER_MODEL),
        ),
    ]
