from django.urls import path
from .views import *

from . import views

urlpatterns = [
    path('new/', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('<int:pk>/update/', views.group_profile, name='group_profile'),
    path('<int:pk>/delete/', views.group_delete, name='group_delete'),
    path('', GroupsListView.as_view(), name='groups_list_view'),
    path('<str:username>/groups/', UserGroupsListView.as_view(), name='user_groups_list_view'), 

    path('follow_group/<int:pk>/', views.follow_group, name='follow_group'),

    path('group_membership/<str:username>/<int:pk>/', views.group_membership, name='group_membership'),
    path('<int:group_id>/request/membership/', views.request_membership, name='request_membership'),
    path('<str:username>/<int:group_id>/request/membership/withdraw/', views.withdraw_membership_request, name='withdraw_membership_request'),
    path('<str:username>/<int:group_id>/request/membership/accept/', views.accept_membership_request, name='accept_membership_request'),

]
