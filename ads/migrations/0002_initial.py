# Generated by Django 4.0.6 on 2022-11-02 13:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('market', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0002_post_group'),
        ('ecoles', '0001_initial'),
        ('ads', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='adpurchase',
            name='listing_to_be_advertised',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='listing_to_be_advertised', to='market.listing'),
        ),
        migrations.AddField(
            model_name='adpurchase',
            name='offer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ad_offer', to='ads.adoffer'),
        ),
        migrations.AddField(
            model_name='adpurchase',
            name='post_to_be_advertised',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='post_to_be_advertised', to='posts.post'),
        ),
        migrations.AddField(
            model_name='adpurchase',
            name='specialization_to_be_advertised',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specialization_to_be_advertised', to='ecoles.specialization'),
        ),
        migrations.AddField(
            model_name='adpurchase',
            name='unique_impressions',
            field=models.ManyToManyField(blank=True, default=None, related_name='unique_impressions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='adpurchase',
            name='user_that_purchased_ad',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_that_purchased_ad', to=settings.AUTH_USER_MODEL),
        ),
    ]
