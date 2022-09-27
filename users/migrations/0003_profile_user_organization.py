# Generated by Django 4.0.6 on 2022-09-26 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('users', '0002_profile_country_twitterhandle_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='user_organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.group'),
        ),
    ]
