# Generated by Django 4.0.6 on 2022-11-28 23:14

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
            name='DirectMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_sent', models.DateTimeField(auto_now_add=True)),
                ('body', models.TextField(default='')),
                ('seen', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True)),
                ('description', models.CharField(blank=True, max_length=256, null=True)),
                ('membership_requesters', models.ManyToManyField(blank=True, default=None, related_name='membership_requesters', to=settings.AUTH_USER_MODEL)),
                ('room_creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_creator', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RoomMembershipRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_requested', models.DateTimeField(auto_now_add=True)),
                ('room_receiving_membership_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_receiving_membership_request', to='messaging.room')),
                ('user_requesting_to_become_room_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_requesting_to_become_room_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
