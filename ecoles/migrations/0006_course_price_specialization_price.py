# Generated by Django 4.0.6 on 2022-09-15 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecoles', '0005_alter_assignmentnote_visibility_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='specialization',
            name='price',
            field=models.IntegerField(default=0),
        ),
    ]