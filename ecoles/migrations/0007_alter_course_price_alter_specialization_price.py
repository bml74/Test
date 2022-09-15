# Generated by Django 4.0.6 on 2022-09-15 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecoles', '0006_course_price_specialization_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='price',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='specialization',
            name='price',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
