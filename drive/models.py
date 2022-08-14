from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.utils import timezone
from config.choices import Languages



class Folder(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent_folder = models.ForeignKey(to='drive.Folder', on_delete=models.CASCADE, related_name="folder_parent_folder", blank=True, null=True)

    def __str__(self):
        return self.title


class UserNote(models.Model):
    title = models.CharField(max_length=100) 
    content = models.TextField(blank=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_note_creator")
    parent_folder = models.ForeignKey(to='drive.Folder', on_delete=models.CASCADE, related_name="usernote_parent_folder", blank=True, null=True)
        
    def __str__(self):
        return self.title



