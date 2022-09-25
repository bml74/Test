from .choices import Visibility, DifficultyLevel
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.utils import timezone
from languages.models import CorsicanBibleChapter
from config.choices import Languages
from django.core.validators import MinValueValidator


class Ecole(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    url_keyword = models.CharField(max_length=16, default="")
    svg_url = models.CharField(max_length=256, default="")
    students = models.ManyToManyField(User, related_name="ecole_students", default=None, blank=True)

    def __str__(self):
        return self.title


# Specializations and Courses:
# Instead of Category and Field being Foreign Keys, they should be ManyToManys, because there
# can be multiple ones for each.


class Category(models.Model):
    title = models.CharField(max_length=64, default="Category", blank=False, unique=True)
    description = models.TextField(blank=False, validators=[MinLengthValidator(10)])

    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator_of_category")

    students = models.ManyToManyField(User, related_name="category_students", default=None, blank=True)
    allowed_editors = models.ManyToManyField(User, related_name="category_allowed_editors", default=None, blank=True)
    edit_access_request = models.ManyToManyField(User, related_name="category_edit_access_request", default=None, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'pk': self.pk})


class Field(models.Model):
    title = models.CharField(max_length=64, default="Field", blank=False, unique=True)
    description = models.TextField(blank=False, validators=[MinLengthValidator(10)])

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
    title = models.CharField(max_length=64, default="Specialization", blank=False, unique=True)
    description = models.TextField(blank=False, validators=[MinLengthValidator(10)])
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
    field = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, related_name="specializations_within_field")
    # schools = models.ManyToManyField(Ecole, null=True, blank=True, related_name="schools_that_specialization_belongs_to")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator_of_specialization")
    students = models.ManyToManyField(User, related_name="specialization_students", default=None, blank=True)
    purchasers = models.ManyToManyField(User, related_name="specialization_purchasers", default=None, blank=True)
    allowed_editors = models.ManyToManyField(User, related_name="specialization_allowed_editors", default=None, blank=True)
    edit_access_request = models.ManyToManyField(User, related_name="specialization_edit_access_request", default=None, blank=True)
    completed = models.ManyToManyField(User, related_name="specialization_completed", default=None, blank=True)
    price = models.FloatField(default=0, validators=[MinValueValidator(0.0)])

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('specialization_detail', kwargs={'pk': self.pk})


class Course(models.Model):
    title = models.CharField(max_length=64, default="Course", blank=False, unique=True)
    description = models.TextField(blank=False, validators=[MinLengthValidator(10)])
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
    field = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, related_name="courses_within_field")
    # schools = models.ManyToManyField(Ecole, null=True, related_name="schools_that_course_belongs_to")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator_of_course")
    specialization = models.ForeignKey(Specialization, on_delete=models.CASCADE, null=True, blank=True, related_name="courses_within_specialization")
    students = models.ManyToManyField(User, related_name="course_students", default=None, blank=True)
    purchasers = models.ManyToManyField(User, related_name="course_purchasers", default=None, blank=True)
    allowed_editors = models.ManyToManyField(User, related_name="course_allowed_editors", default=None, blank=True)
    edit_access_request = models.ManyToManyField(User, related_name="course_edit_access_request", default=None, blank=True)
    completed = models.ManyToManyField(User, related_name="course_completed", default=None, blank=True)
    price = models.FloatField(default=0, validators=[MinValueValidator(0.0)])

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'pk': self.pk})


class Module(models.Model):
    title = models.CharField(max_length=64, default="Module", blank=False)
    description = models.TextField(blank=False, validators=[MinLengthValidator(10)])
    # visibility = models.CharField(
    #     max_length=100,
    #     choices=Visibility.choices,
    #     default=Visibility.PRIVATE,
    #     blank=False,
    # )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules_within_course")

    completed = models.ManyToManyField(
        User,
        related_name="module_completed",
        default=None,
        blank=True
    )

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('module_detail', kwargs={'pk': self.pk, "course_id": self.course.id})


class Submodule(models.Model):
    title = models.CharField(max_length=128, default="Submodule", blank=False)
    description = models.TextField(blank=False, validators=[MinLengthValidator(10)])

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="submodules_within_module")

    completed = models.ManyToManyField(
        User,
        related_name="submodule_completed",
        default=None,
        blank=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('submodule_detail', kwargs={'pk': self.pk, "course_id": self.module.course.id, "module_id": self.module.id})


class Assignment(models.Model):
    title = models.CharField(max_length=256, default="Assignment", blank=False)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True, default=timezone.now)
    estimated_minutes_to_complete = models.FloatField(default=30)

    language = models.CharField(max_length=64, choices=Languages.choices, default=Languages.ENGLISH, blank=True)

    assignment_type = models.CharField(
        max_length=100, 
        choices=(
            ("Choose an assignment type", "Choose an assignment type"), # Just text on the page itself
            ("Text", "Text"), # Just text on the page itself
            ("Internal Link", "Internal Link"), # ex. Link to a YouTube transcript on our site or to a News Search article
            ("External Reading Link", "External Reading Link"), # ex. Link to an article on another site
            ("External Link", "External Link"), # ex. link to any other page from another site, such as PDF, for example
            # ("Internal PDF", "Internal PDF"), # PDF on site
            # ("Writing Entry", "Writing Entry"), # Like a journal or diary, but for something specific
            # ("Exam", "Exam"), # Quiz/test
            # ("Language Session", "Language Session"), # Like a Duolingo lesson; basically a slideshow of questions
            # ("Slideshow", "Slideshow"), # Powerpoint of Google Slides presentation
            # ("File", "File"), # User can upload file
            # ("Stories", "Stories"), # Like TikTok/Instagram/YouTube stories
            # ("Table", "Table"), # ex. for Grammar tables verb endings
            # ("Audio", "Audio"), # Audio file
            ("Iframe Link", "Iframe Link"), # Iframe 
            ("Corsican Bible Chapter", "Corsican Bible Chapter"),
            ("Youtube Video Link", "Youtube Video Link"),
            ("Youtube Video Transcript ID", "Youtube Video Transcript ID"),
            # ("PDF Link", "PDF Link"),
            # ("Image", "Image")
            ("Article", "Article"),
        ),
        default="Choose an assignment type",
        blank=False,
    )
    text = models.TextField(blank=True, null=True) # For assignment choice: Text
    internal_link = models.CharField(max_length=255, default="#", blank=True, null=True) # For assignment choice: Internal Link
    external_reading_link = models.CharField(max_length=255, default="#", blank=True, null=True) # For assignment choice: External Reading
    external_link = models.CharField(max_length=255, default="#", blank=True, null=True) # For assignment choice: External Link
    # internal_pdf = models.ABC123Field(blank=True, null=True) # For assignment choice: Internal PDF
    # writing_entry
    # exam
    # language_session
    # slideshow
    # file
    # stories
    # table
    # audio
    iframe_link = models.CharField(max_length=255, default="#", blank=True, null=True) # For assignment choice: IFrame

    corsican_bible_chapter = models.ForeignKey(CorsicanBibleChapter, on_delete=models.CASCADE, related_name="corsican_bible_chapter_assignment", blank=True, null=True)
    
    youtube_video_link = models.CharField(max_length=255, default="#", blank=True, null=True) # For assignment choice: Youtube Video Link
    youtube_video_transcript_id = models.CharField(max_length=127, default="#", blank=True, null=True) # For assignment choice: Youtube Video Transcript ID

    article_by_url = models.BooleanField(blank=True, null=True)
    article_id = models.IntegerField(blank=True, null=True)

    completed = models.ManyToManyField(
        User,
        related_name="assignment_completed",
        default=None,
        blank=True
    )

    submodule = models.ForeignKey(Submodule, on_delete=models.CASCADE, related_name="assignments_within_submodule")

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('assignment_detail', kwargs={'pk': self.pk, "course_id": self.submodule.module.course.id, "module_id": self.submodule.module.id, "submodule_id": self.submodule.id})


class Task(models.Model):
    task_type = models.CharField( 
        max_length=15,
        choices=(("Read", "Read"), ("Watch", "Watch"), ("Notes", "Notes"), ("Write", "Write")),
        default="Read",
        blank=False,
    )

    due_date = models.DateTimeField(auto_now_add=True)

    assignment = models.ForeignKey(Assignment, null=True, blank=True, on_delete=models.CASCADE, related_name="tasks_within_assignment")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="creator_of_task")

    completed = models.ManyToManyField(
        User,
        related_name="task_completed",
        default=None,
        blank=True
    )

    def __str__(self):
        return self.task_type
    
    def get_absolute_url(self):
        return reverse('task_detail', kwargs={"course_id": self.assignment.submodule.module.course.id, "module_id": self.assignment.submodule.module.id, "submodule_id": self.assignment.submodule.id, "assignment_id": self.assignment.id, 'pk': self.pk, "username": self.creator.username})


class AssignmentNote(models.Model):
    title = models.CharField(max_length=100) 
    content = models.TextField(blank=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="assignment_note")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignment_note_creator")
    visibility = models.CharField(
        max_length=100,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
        blank=False,
        null=False
    )
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('malagosto_assignments_detail', kwargs={'pk': self.assignment.pk})


