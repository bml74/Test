# Generated by Django 4.0.6 on 2022-09-06 18:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TwitterHandle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twitter_handle', models.CharField(blank=True, max_length=256, null=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_twitter_handle', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('num_credits', models.IntegerField(default=0)),
                ('verified_course_creator', models.BooleanField(default=False)),
                ('select_view_seen', models.BooleanField(default=False)),
                ('primary_twitter_handle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.twitterhandle')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FollowersCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower_of_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='follower_of_user', to=settings.AUTH_USER_MODEL)),
                ('user_being_followed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_being_followed', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
