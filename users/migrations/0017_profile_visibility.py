# Generated by Django 4.0.6 on 2022-10-22 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_remove_profile_select_view_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='visibility',
            field=models.CharField(choices=[('Public', 'Public'), ('Private', 'Private')], default='Public', max_length=8),
        ),
    ]
