from django.db import models
from django.contrib.auth.models import User
import random

DIFF_CHOICES = (
    ('Easy', 'Easy'),
    ('Medium', 'Medium'),
    ('Hard', 'Hard'),
)

class Quiz(models.Model):
    name = models.CharField(max_length=120)
    topic = models.CharField(max_length=120)
    number_of_questions = models.IntegerField()
    time = models.IntegerField(help_text="duration of the quiz in minutes")
    required_score_to_pass = models.IntegerField(help_text="required score in %")
    difficulty = models.CharField(max_length=6, choices=DIFF_CHOICES)
    assignment = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='quiz_assignment')
    article_id = models.IntegerField(blank=True, null=True)
    article_by_url = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_questions(self):
        questions = list(self.question_set.all())
        random.shuffle(questions)
        return questions[:self.number_of_questions]

    class Meta:
        verbose_name_plural = 'Quizzes'


class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results_regarding_quiz')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='results_of_user')
    score = models.FloatField()

    def __str__(self):
        return f"Score of {self.score} on quiz {self.quiz.name} for user {self.user.username}"

