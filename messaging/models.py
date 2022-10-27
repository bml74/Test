from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DirectMessage(models.Model):
    date_time_sent = models.DateTimeField(auto_now_add=True)
    body = models.TextField(default="")
    sender_of_message = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_of_message")
    receiver_of_message = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver_of_message")
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Message sent by {self.sender_of_message} to {self.receiver_of_message}"