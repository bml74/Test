# Generated by Django 4.0.6 on 2022-08-15 16:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecoles', '0003_assignment_language_alter_category_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='field',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses_within_field', to='ecoles.field'),
        ),
    ]
