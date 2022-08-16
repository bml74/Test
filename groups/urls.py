# from django.urls import path
# from .views import *

# from . import views

# urlpatterns = [
#     path('followers_count/', views.followers_count, name='followers_count'),
#     path('groups/new/', views.GroupCreateView.as_view(), name='group_create'),
#     path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
#     path('groups/<int:pk>/update/', views.group_profile, name='group_profile'),
#     path('groups/<int:pk>/delete/', views.group_delete, name='group_delete'),
#     path('groups/', GroupsListView.as_view(), name='groups_list_view'),
#     path('<str:username>/groups/', UserGroupsListView.as_view(), name='user_groups_list_view'), # List view for all groups that the user is in.
#     path('group_followers_count/', views.group_followers_count, name='group_followers_count'),
# ]