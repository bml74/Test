# Generated by Django 4.0.6 on 2022-08-02 12:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0006_alter_articlebytitle_url_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchAccessRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_requested', models.DateTimeField(auto_now_add=True)),
                ('requester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
