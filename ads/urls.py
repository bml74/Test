from django.urls import path
from .views import *

from . import views

urlpatterns = [
    path('test/', views.test, name='test'),
]