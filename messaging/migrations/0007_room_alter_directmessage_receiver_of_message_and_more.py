# Generated by Django 4.0.6 on 2022-11-02 16:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('messaging', '0006_alter_directmessage_date_time_sent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.AlterField(
            model_name='directmessage',
            name='receiver_of_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver_of_message', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='directmessage',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='receiver_of_message', to='messaging.room'),
        ),
    ]
