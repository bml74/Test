# Generated by Django 4.0.6 on 2022-11-28 23:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


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
            name='ReferralCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referral_code', models.CharField(blank=True, max_length=16, null=True, unique=True)),
                ('generatedBy', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='generatedBy', to=settings.AUTH_USER_MODEL)),
                ('usedBy', models.ManyToManyField(blank=True, default=None, related_name='usedBy', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('credits', models.IntegerField(default=0)),
                ('verified_creator', models.BooleanField(default=False)),
                ('has_super_status', models.BooleanField(default=False)),
                ('country', django_countries.fields.CountryField(default='US', max_length=2)),
                ('hasUsedAReferralCode', models.BooleanField(default=False)),
                ('visibility', models.CharField(choices=[('Public', 'Public'), ('Private', 'Private')], default='Public', max_length=8)),
                ('ACCOUNT_BALANCE', models.IntegerField(default=0)),
                ('primary_twitter_handle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.twitterhandle')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FollowRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_requested', models.DateTimeField(auto_now_add=True)),
                ('user_receiving_follow_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_receiving_follow_request', to=settings.AUTH_USER_MODEL)),
                ('user_requesting_to_follow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_requesting_to_follow', to=settings.AUTH_USER_MODEL)),
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
