# Generated by Django 4.0.6 on 2022-08-13 16:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folder',
            name='parent_folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='drive_parent_folder', to='drive.folder'),
        ),
    ]