# Generated by Django 4.0.6 on 2022-11-11 15:25

from django.conf import settings
import django.core.validators
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
            name='AdOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(default='Ad Offer', max_length=64, unique=True)),
                ('description', models.TextField(default='Description for ad offer')),
                ('price', models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('metric', models.CharField(choices=[('Impressions', 'Impressions'), ('Unique Impressions', 'Unique Impressions'), ('Clicks', 'Clicks')], default='Impressions', max_length=32)),
                ('required_ad_impressions', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('required_unique_ad_impressions', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('required_clicks', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='AdPurchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('clicks', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('impressions', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('advertisement_type', models.CharField(choices=[('Specialization', 'Specialization'), ('Course', 'Course'), ('Post', 'Post'), ('Listing', 'Listing'), ('General Advertisement', 'General Advertisement')], default='General Advertisement', max_length=32)),
                ('general_advertisement_text', models.CharField(blank=True, max_length=128, null=True)),
                ('group_that_purchased_ad', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_that_purchased_ad', to='auth.group')),
                ('offer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ad_offer', to='ads.adoffer')),
                ('unique_impressions', models.ManyToManyField(blank=True, default=None, related_name='unique_impressions', to=settings.AUTH_USER_MODEL)),
                ('user_that_purchased_ad', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_that_purchased_ad', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
