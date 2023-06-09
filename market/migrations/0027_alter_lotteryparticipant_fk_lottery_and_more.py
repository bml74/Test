# Generated by Django 4.0.6 on 2023-01-14 22:43

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0026_alter_suggesteddelivery_suggested_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lotteryparticipant',
            name='fk_lottery',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='fk_lottery', to='market.lottery'),
        ),
        migrations.AlterField(
            model_name='suggesteddelivery',
            name='suggested_date_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 1, 14, 22, 43, 8, 780813, tzinfo=utc)),
        ),
    ]
