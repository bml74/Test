from django.db.models import TextChoices


class Visibility(TextChoices):
    # INVISIBLE = 'Invisible'
    PRIVATE = 'Private'
    PUBLIC = 'Public'
    # ANONYMOUS = 'Anonymous'


class DifficultyLevel(TextChoices):
    BEGINNER = 'Beginner'
    MIXED = 'Mixed'
    INTERMEDIATE = 'Intermediate'
    DIFFICULT = 'Difficult'
    ADVANCED = "Advanced"