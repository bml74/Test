# Generated by Django 4.0.6 on 2022-09-13 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0003_listing_visibility'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='listing_type',
            field=models.CharField(choices=[('General', 'General'), ('Homework', 'Homework'), ('Consulting', 'Consulting'), ('Tutoring', 'Tutoring'), ('Sale', 'Sale')], default='General', max_length=100),
        ),
        migrations.AlterField(
            model_name='listing',
            name='visibility',
            field=models.CharField(choices=[('Invisible', 'Invisible'), ('Private', 'Private'), ('Public', 'Public'), ('Anonymous', 'Anonymous')], default='Anonymous', max_length=100),
        ),
    ]
