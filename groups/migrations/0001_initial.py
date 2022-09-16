# Generated by Django 4.0.6 on 2022-09-16 14:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('group_visibility', models.CharField(choices=[('Invisible', 'Invisible'), ('Private', 'Private'), ('Public', 'Public')], default='Private', max_length=64)),
                ('group_type', models.CharField(choices=[('Group', 'Group'), ('Club', 'Club'), ('Business', 'Business'), ('Nonprofit', 'Nonprofit'), ('Graduate School', 'Graduate School'), ('University', 'University'), ('High School', 'High School'), ('Middle School', 'Middle School'), ('Elementary School', 'Elementary School'), ('Other', 'Other')], default='Group', max_length=64)),
                ('group', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='auth.group')),
                ('group_creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_creator', to=settings.AUTH_USER_MODEL)),
                ('group_members', models.ManyToManyField(blank=True, default=None, related_name='group_members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GroupFollowersCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower_of_group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='follower_of_group', to=settings.AUTH_USER_MODEL)),
                ('group_being_followed', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_being_followed', to='auth.group')),
            ],
        ),
    ]
