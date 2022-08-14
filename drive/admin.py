from re import U
from django.contrib import admin
from .models import Folder, UserNote


admin.site.register(Folder)
admin.site.register(UserNote)
