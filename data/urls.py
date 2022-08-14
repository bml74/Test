from . import views
from users import views as user_views

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('d3/hierarchy/', views.d3_org_tree, name='d3_org_tree'),
    path('d3/tree/1/', views.d3_tree_1, name='d3_tree_1'),
    path('d3/networks/money/', views.d3_money_network, name='d3_money_network'),
]
