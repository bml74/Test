from django.urls import path
from .views import *

from . import views

urlpatterns = [
    path('followers_count/', views.followers_count, name='followers_count'),
    path('follow_request/<str:user_requesting_to_follow>/<str:user_receiving_follow_request>/', views.follow_request, name='follow_request'),
    path('accept_follow_request/<str:user_requesting_to_follow>/<str:user_receiving_follow_request>/', views.accept_follow_request, name='accept_follow_request'),
    path('withdraw_follow_request/<str:user_requesting_to_follow>/<str:user_receiving_follow_request>/', views.withdraw_follow_request, name='withdraw_follow_request'),
]