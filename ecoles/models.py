from .choices import Visibility, DifficultyLevel
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class Ecole(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    url_keyword = models.CharField(max_length=16, default="")
    svg_url = models.CharField(max_length=256, default="")

    def __str__(self):
        return self.title

# Specializations and Courses:
# Instead of Category and Field being Foreign Keys, they should be ManyToManys, because there
# can be multiple ones for each.

class Category(models.Model):
    title = models.CharField(max_length=64, default="Category", blank=False)
    description = models.TextField(blank=False, validators=[MinLengthValidator(30)])

    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator_of_category")

    students = models.ManyToManyField(User, related_name="category_students", default=None, blank=True)
    allowed_editors = models.ManyToManyField(User, related_name="category_allowed_editors", default=None, blank=True)
    edit_access_request = models.ManyToManyField(User, related_name="category_edit_access_request", default=None, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})


class Field(models.Model):
    title = models.CharField(max_length=64, default="Field", blank=False)
    description = models.TextField(blank=False, validators=[MinLengthValidator(30)])

    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name="category_of_field")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator_of_field")
    
    students = models.ManyToManyField(User, related_name="field_students", default=None, blank=True)
    allowed_editors = models.ManyToManyField(User, related_name="field_allowed_editors", default=None, blank=True)
    edit_access_request = models.ManyToManyField(User, related_name="field_edit_access_request", default=None, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('field_detail', kwargs={'pk': self.pk})


class Specialization(models.Model):
    # Reminder: if user enrolls in specialization, then they are 
    # automatically enrolled in all courses beloging to the specialization.
    title = models.CharField(max_length=64, default="Specialization", blank=False)
    description = models.TextField(blank=False, validators=[MinLengthValidator(30)])
    visibility = models.CharField(
        max_length=100,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
        blank=False,
        null=False
    )
    difficulty_level = models.CharField(
        max_length=100,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER,
        blank=False,
    )

    # Make Category/Field ManyToMany instead of ForeignKey???
    # field = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, related_name="specializations_within_field")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator_of_specialization")
    students = models.ManyToManyField(User, related_name="specialization_students", default=None, blank=True)
    allowed_editors = models.ManyToManyField(User, related_name="specialization_allowed_editors", default=None, blank=True)
    edit_access_request = models.ManyToManyField(User, related_name="specialization_edit_access_request", default=None, blank=True)
    completed = models.ManyToManyField(User, related_name="specialization_completed", default=None, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('specialization_detail', kwargs={'pk': self.pk})


class Course(models.Model):
    title = models.CharField(max_length=64, default="Course", blank=False)
    description = models.TextField(blank=False, validators=[MinLengthValidator(30)])
    visibility = models.CharField(
        max_length=100,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
        blank=False,
        null=False
    )
    difficulty_level = models.CharField(
        max_length=100,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER,
        blank=False,
    )

    # Make Category/Field ManyToMany instead of ForeignKey???
    # field = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, related_name="courses_within_field")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator_of_course")
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, null=True, blank=True, related_name="courses_within_specialization")
    students = models.ManyToManyField(User, related_name="course_students", default=None, blank=True)
    allowed_editors = models.ManyToManyField(User, related_name="course_allowed_editors", default=None, blank=True)
    edit_access_request = models.ManyToManyField(User, related_name="course_edit_access_request", default=None, blank=True)
    completed = models.ManyToManyField(User, related_name="course_completed", default=None, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.pk})


