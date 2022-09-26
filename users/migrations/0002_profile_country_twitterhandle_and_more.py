# Generated by Django 4.0.6 on 2022-09-26 13:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='country',
            field=django_countries.fields.CountryField(default='US', max_length=2),
        ),
        migrations.CreateModel(
            name='TwitterHandle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter_handle', models.CharField(blank=True, max_length=256, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_twitter_handle', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='primary_twitter_handle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.twitterhandle'),
        ),
    ]
