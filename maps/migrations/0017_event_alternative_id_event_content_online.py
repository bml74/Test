# Generated by Django 4.0.6 on 2022-10-26 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0016_alter_event_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='alternative_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='event',
            name='content_online',
            field=models.BooleanField(default=False),
        ),
    ]