# Generated by Django 4.0.6 on 2023-02-01 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecoles', '0003_alter_assignmentnote_visibility_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentnote',
            name='visibility',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Anonymous', 'Anonymous')], default='Private', max_length=100),
        ),
        migrations.AlterField(
            model_name='course',
            name='visibility',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Anonymous', 'Anonymous')], default='Private', max_length=100),
        ),
        migrations.AlterField(
            model_name='specialization',
            name='visibility',
            field=models.CharField(choices=[('Private', 'Private'), ('Public', 'Public'), ('Anonymous', 'Anonymous')], default='Private', max_length=100),
        ),
    ]
