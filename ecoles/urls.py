from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [

    path('', views.ecoles_home, name='ecoles-home'),

    path('courseinfo/', views.course_info_design, name='course-info-design'),
    path('course/', views.course_design, name='course-design'),

]
