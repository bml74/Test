# Generated by Django 4.0.6 on 2022-09-26 22:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_profile_user_organization'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user_organization',
        ),
    ]
