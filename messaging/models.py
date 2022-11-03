from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from orgs.models import GroupProfile
from django.urls import reverse


class Room(models.Model):
    title = models.CharField(max_length=128, unique=True)
    room_creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="room_creator")
    room_group_profile = models.ForeignKey(GroupProfile, on_delete=models.CASCADE, blank=True, null=True, related_name="room_group_profile")
    room_members = models.ManyToManyField(User, related_name="room_members", default=None, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('room-detail', kwargs={'pk': self.pk})

    


class RoomMembershipRequest(models.Model):
    date_time_requested = models.DateTimeField(auto_now_add=True) 
    user_requesting_to_become_room_member = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_requesting_to_become_room_member") 
    room_receiving_membership_request = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_receiving_membership_request") 



class DirectMessage(models.Model):
    date_time_sent = models.DateTimeField(auto_now_add=True)
    body = models.TextField(default="")
    sender_of_message = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_of_message")
    receiver_of_message = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="receiver_of_message")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True, related_name="receiver_of_message")
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"Message sent by {self.sender_of_message} to {self.receiver_of_message}"

