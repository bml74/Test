from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, Group


class Review(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    subject = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subject_of_review')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_of_review')

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('review-detail', kwargs={'pk': self.pk})

