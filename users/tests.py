import string, random
from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class UserTestCase(TestCase):

    def getUsername(self):
        return "myTestUser"

    def setUp(self):
        username = self.getUsername()
        User.objects.create(username=username)

    def userCreatedSuccessfully(self):
        username = self.getUsername()
        user = User.objects.get(username=username)
        self.assertEqual(user.username, username)

