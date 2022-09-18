# Generated by Django 4.0.6 on 2022-09-17 15:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('market', '0009_rename_transaction_obj_type_id_transaction_transaction_obj_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='seller',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='seller', to=settings.AUTH_USER_MODEL),
        ),
    ]
