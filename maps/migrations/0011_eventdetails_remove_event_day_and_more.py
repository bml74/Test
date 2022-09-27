# Generated by Django 4.0.6 on 2022-09-26 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0010_event_address_event_district_event_neighborhood_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('number_of_sub_sites', models.IntegerField(blank=True, default=1, null=True)),
                ('number_of_casualties', models.IntegerField(blank=True, default=1, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='event',
            name='day',
        ),
        migrations.RemoveField(
            model_name='event',
            name='description',
        ),
        migrations.RemoveField(
            model_name='event',
            name='details_available',
        ),
        migrations.RemoveField(
            model_name='event',
            name='number_of_casualties',
        ),
        migrations.RemoveField(
            model_name='event',
            name='number_of_sub_sites',
        ),
    ]