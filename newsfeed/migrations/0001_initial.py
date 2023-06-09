# Generated by Django 4.0.6 on 2022-11-28 23:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Feed', max_length=64)),
                ('url', models.CharField(default='', max_length=1024)),
                ('category', models.CharField(blank=True, max_length=64)),
                ('followers', models.ManyToManyField(blank=True, default=None, related_name='feed_followers', to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feed_source', to='news.source')),
            ],
        ),
    ]
