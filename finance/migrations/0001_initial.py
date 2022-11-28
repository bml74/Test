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
            name='Chain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('date_entered', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('date_entered', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_entered'],
            },
        ),
        migrations.CreateModel(
            name='Era',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('date_entered', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('date_entered', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TwoSidedFinancialTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_1', models.CharField(max_length=256)),
                ('type_of_asset_received_by_entity_1', models.CharField(blank=True, choices=[('Cash', 'Cash'), ('Credit', 'Credit'), ('Real Estate', 'Real Estate'), ('Stock', 'Stock'), ('Bond', 'Bond'), ('Physical Asset', 'Physical Asset'), ('Painting', 'Painting'), ('Arms', 'Arms'), ('Other', 'Other')], default='Cash', max_length=64, null=True)),
                ('description_of_asset_received_by_entity_1', models.CharField(max_length=256)),
                ('monetary_value_of_asset_received_by_entity_1', models.FloatField(default=0.0)),
                ('monetary_value_of_asset_received_by_entity_1_is_estimated', models.BooleanField(default=False)),
                ('currency_of_asset_received_by_entity_1_if_applicable', models.CharField(blank=True, choices=[('USD', 'USD'), ('RUB', 'RUB'), ('EUR', 'EUR'), ('AUD', 'AUD'), ('CAD', 'CAD'), ('CNY', 'CNY'), ('JPY', 'JPY')], default=None, max_length=8, null=True)),
                ('entity_2', models.CharField(max_length=256)),
                ('type_of_asset_received_by_entity_2', models.CharField(blank=True, choices=[('Cash', 'Cash'), ('Credit', 'Credit'), ('Real Estate', 'Real Estate'), ('Stock', 'Stock'), ('Bond', 'Bond'), ('Physical Asset', 'Physical Asset'), ('Painting', 'Painting'), ('Arms', 'Arms'), ('Other', 'Other')], default='Cash', max_length=64, null=True)),
                ('description_of_asset_received_by_entity_2', models.CharField(max_length=256)),
                ('monetary_value_of_asset_received_by_entity_2', models.FloatField(default=0.0)),
                ('monetary_value_of_asset_received_by_entity_2_is_estimated', models.BooleanField(default=False)),
                ('currency_of_asset_received_by_entity_2_if_applicable', models.CharField(blank=True, choices=[('USD', 'USD'), ('RUB', 'RUB'), ('EUR', 'EUR'), ('AUD', 'AUD'), ('CAD', 'CAD'), ('CNY', 'CNY'), ('JPY', 'JPY')], default='USD', max_length=8, null=True)),
                ('crime', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True, null=True)),
                ('transaction_date', models.DateTimeField(blank=True, null=True)),
                ('date_entered', models.DateTimeField(auto_now_add=True, null=True)),
                ('citation', models.TextField(blank=True, null=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('chains', models.ManyToManyField(blank=True, default=None, related_name='transaction_chains', to='finance.chain')),
                ('entities', models.ManyToManyField(blank=True, default=None, related_name='transaction_entities', to='finance.entity')),
                ('eras', models.ManyToManyField(blank=True, default=None, related_name='transaction_eras', to='finance.era')),
                ('themes', models.ManyToManyField(blank=True, default=None, related_name='transaction_themes', to='finance.theme')),
            ],
        ),
    ]
