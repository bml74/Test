# Generated by Django 4.0.6 on 2022-08-09 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0004_set_description_set_from_language_set_to_language_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Definition',
        ),
        migrations.DeleteModel(
            name='Translation',
        ),
    ]
