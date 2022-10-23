# Generated by Django 4.0.6 on 2022-10-22 16:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orgs', '0002_groupprofile_group_followers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupprofile',
            name='group_visibility',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public')], default='Private', max_length=64),
        ),
        migrations.CreateModel(
            name='GroupMembershipRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_requested', models.DateTimeField(auto_now_add=True)),
                ('group_receiving_membership_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_receiving_membership_request', to='auth.group')),
                ('user_requesting_to_become_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_requesting_to_become_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupFollowRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_requested', models.DateTimeField(auto_now_add=True)),
                ('group_receiving_follow_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_receiving_follow_request', to='auth.group')),
                ('user_requesting_to_follow_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_requesting_to_follow_group', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]