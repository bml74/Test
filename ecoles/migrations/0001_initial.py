# Generated by Django 4.0.6 on 2022-08-09 17:08

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('languages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Assignment', max_length=256)),
                ('description', models.TextField(blank=True)),
                ('due_date', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('estimated_minutes_to_complete', models.FloatField(default=30)),
                ('assignment_type', models.CharField(choices=[('Choose an assignment type', 'Choose an assignment type'), ('Text', 'Text'), ('Internal Link', 'Internal Link'), ('External Reading Link', 'External Reading Link'), ('External Link', 'External Link'), ('Iframe Link', 'Iframe Link'), ('Corsican Bible Chapter', 'Corsican Bible Chapter'), ('Youtube Video Link', 'Youtube Video Link'), ('Youtube Video Transcript ID', 'Youtube Video Transcript ID')], default='Choose an assignment type', max_length=100)),
                ('text', models.TextField(blank=True, null=True)),
                ('internal_link', models.CharField(blank=True, default='#', max_length=255, null=True)),
                ('external_reading_link', models.CharField(blank=True, default='#', max_length=255, null=True)),
                ('external_link', models.CharField(blank=True, default='#', max_length=255, null=True)),
                ('iframe_link', models.CharField(blank=True, default='#', max_length=255, null=True)),
                ('youtube_video_link', models.CharField(blank=True, default='#', max_length=255, null=True)),
                ('youtube_video_transcript_id', models.CharField(blank=True, default='#', max_length=127, null=True)),
                ('completed', models.ManyToManyField(blank=True, default=None, related_name='assignment_completed', to=settings.AUTH_USER_MODEL)),
                ('corsican_bible_chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='corsican_bible_chapter_assignment', to='languages.corsicanbiblechapter')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Category', max_length=64)),
                ('description', models.TextField(validators=[django.core.validators.MinLengthValidator(30)])),
                ('allowed_editors', models.ManyToManyField(blank=True, default=None, related_name='category_allowed_editors', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator_of_category', to=settings.AUTH_USER_MODEL)),
                ('edit_access_request', models.ManyToManyField(blank=True, default=None, related_name='category_edit_access_request', to=settings.AUTH_USER_MODEL)),
                ('students', models.ManyToManyField(blank=True, default=None, related_name='category_students', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Course', max_length=64)),
                ('description', models.TextField(validators=[django.core.validators.MinLengthValidator(30)])),
                ('visibility', models.CharField(choices=[('Invisible', 'Invisible'), ('Private', 'Private'), ('Public', 'Public')], default='Private', max_length=100)),
                ('difficulty_level', models.CharField(choices=[('Beginner', 'Beginner'), ('Mixed', 'Mixed'), ('Intermediate', 'Intermediate'), ('Difficult', 'Difficult'), ('Advanced', 'Advanced')], default='Beginner', max_length=100)),
                ('allowed_editors', models.ManyToManyField(blank=True, default=None, related_name='course_allowed_editors', to=settings.AUTH_USER_MODEL)),
                ('completed', models.ManyToManyField(blank=True, default=None, related_name='course_completed', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator_of_course', to=settings.AUTH_USER_MODEL)),
                ('edit_access_request', models.ManyToManyField(blank=True, default=None, related_name='course_edit_access_request', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ecole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('url_keyword', models.CharField(default='', max_length=16)),
                ('svg_url', models.CharField(default='', max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Field',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Field', max_length=64)),
                ('description', models.TextField(validators=[django.core.validators.MinLengthValidator(30)])),
                ('allowed_editors', models.ManyToManyField(blank=True, default=None, related_name='field_allowed_editors', to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='category_of_field', to='ecoles.category')),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator_of_field', to=settings.AUTH_USER_MODEL)),
                ('edit_access_request', models.ManyToManyField(blank=True, default=None, related_name='field_edit_access_request', to=settings.AUTH_USER_MODEL)),
                ('students', models.ManyToManyField(blank=True, default=None, related_name='field_students', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Module', max_length=64)),
                ('description', models.TextField(validators=[django.core.validators.MinLengthValidator(30)])),
                ('completed', models.ManyToManyField(blank=True, default=None, related_name='module_completed', to=settings.AUTH_USER_MODEL)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules_within_course', to='ecoles.course')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.CharField(choices=[('Read', 'Read'), ('Watch', 'Watch'), ('Notes', 'Notes'), ('Write', 'Write')], default='Read', max_length=15)),
                ('due_date', models.DateTimeField(auto_now_add=True)),
                ('assignment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks_within_assignment', to='ecoles.assignment')),
                ('completed', models.ManyToManyField(blank=True, default=None, related_name='task_completed', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator_of_task', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Submodule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Submodule', max_length=128)),
                ('description', models.TextField(validators=[django.core.validators.MinLengthValidator(30)])),
                ('completed', models.ManyToManyField(blank=True, default=None, related_name='submodule_completed', to=settings.AUTH_USER_MODEL)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submodules_within_module', to='ecoles.module')),
            ],
        ),
        migrations.CreateModel(
            name='Specialization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Specialization', max_length=64)),
                ('description', models.TextField(validators=[django.core.validators.MinLengthValidator(30)])),
                ('visibility', models.CharField(choices=[('Invisible', 'Invisible'), ('Private', 'Private'), ('Public', 'Public')], default='Private', max_length=100)),
                ('difficulty_level', models.CharField(choices=[('Beginner', 'Beginner'), ('Mixed', 'Mixed'), ('Intermediate', 'Intermediate'), ('Difficult', 'Difficult'), ('Advanced', 'Advanced')], default='Beginner', max_length=100)),
                ('allowed_editors', models.ManyToManyField(blank=True, default=None, related_name='specialization_allowed_editors', to=settings.AUTH_USER_MODEL)),
                ('completed', models.ManyToManyField(blank=True, default=None, related_name='specialization_completed', to=settings.AUTH_USER_MODEL)),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='creator_of_specialization', to=settings.AUTH_USER_MODEL)),
                ('edit_access_request', models.ManyToManyField(blank=True, default=None, related_name='specialization_edit_access_request', to=settings.AUTH_USER_MODEL)),
                ('field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='specializations_within_field', to='ecoles.field')),
                ('students', models.ManyToManyField(blank=True, default=None, related_name='specialization_students', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='course',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses_within_field', to='ecoles.field'),
        ),
        migrations.AddField(
            model_name='course',
            name='specialization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='courses_within_specialization', to='ecoles.specialization'),
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, default=None, related_name='course_students', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='AssignmentNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('visibility', models.CharField(choices=[('Invisible', 'Invisible'), ('Private', 'Private'), ('Public', 'Public')], default='Private', max_length=100)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_note', to='ecoles.assignment')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignment_note_creator', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='assignment',
            name='submodule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments_within_submodule', to='ecoles.submodule'),
        ),
    ]
