from django.urls import path
from .views import *

from . import views

urlpatterns = [
    path('new/', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('<int:pk>/update/', views.group_profile, name='group_profile'),
    path('<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('', GroupsListView.as_view(), name='groups_list_view'),
    path('<str:username>/groups/', UserGroupsListView.as_view(), name='user_groups_list_view'), # List view for all groups that the user is in.
    path('follow_group/<int:pk>/', views.follow_group, name='follow_group'),

    path('<int:group_id>/request/membership/', views.request_membership, name='request_membership'),

]