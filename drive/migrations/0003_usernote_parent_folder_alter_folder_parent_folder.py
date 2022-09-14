# Generated by Django 4.0.6 on 2022-08-13 16:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0002_alter_folder_parent_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='usernote',
            name='parent_folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usernote_parent_folder', to='drive.folder'),
        ),
        migrations.AlterField(
            model_name='folder',
            name='parent_folder',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='folder_parent_folder', to='drive.folder'),
        ),
    ]