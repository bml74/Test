# Generated by Django 4.0.6 on 2022-10-24 13:43

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Specialization', max_length=64, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('price', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('price_based_off_of', models.CharField(choices=[('Impressions', 'Impressions'), ('Unique Impressions', 'Unique Impressions'), ('Clicks', 'Clicks')], default='Impressions', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='AdPurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clicks', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('impressions', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('group_that_purchased_ad', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_that_purchased_ad', to='auth.group')),
                ('offer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ad_offer', to='ads.adoffer')),
                ('unique_impressions', models.ManyToManyField(blank=True, default=None, related_name='unique_impressions', to=settings.AUTH_USER_MODEL)),
                ('user_that_purchased_ad', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_that_purchased_ad', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
