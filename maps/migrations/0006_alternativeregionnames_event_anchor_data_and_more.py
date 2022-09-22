# Generated by Django 4.0.6 on 2022-09-21 15:02

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('maps', '0005_event'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlternativeRegionNames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='event',
            name='anchor_data',
            field=models.DateField(default='1945-09-01'),
        ),
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='number_of_casualties',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='number_of_days_after_anchor_date_that_event_began',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='event',
            name='number_of_days_after_anchor_date_that_event_started',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='event',
            name='number_of_sub_sites',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='primary_country_name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='primary_region_name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='maps.AlternativeRegionNames', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='event',
            name='primary_city_name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='alternativeregionnames',
            name='content_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maps.event'),
        ),
        migrations.AddField(
            model_name='alternativeregionnames',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_items', to='taggit.tag'),
        ),
    ]