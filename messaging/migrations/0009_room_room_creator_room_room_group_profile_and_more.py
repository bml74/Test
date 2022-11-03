# Generated by Django 4.0.6 on 2022-11-03 17:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orgs', '0001_initial'),
        ('messaging', '0008_room_room_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='room_creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_creator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='room_group_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='room_group_profile', to='orgs.groupprofile'),
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
