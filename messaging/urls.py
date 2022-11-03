from django.urls import path
from . import views


urlpatterns = [

   	path('', views.inbox, name='inbox'),
	path('direct/message/notification/', views.directMessageNotification, name='direct-message-notification'),
	path('user/<int:pk>/', views.detail, name='detail'),
	path('sent/<int:pk>/', views.sentDirectMessage, name='sent_direct_message'),
	path('received/<int:pk>/', views.receivedDirectMessages, name='received_direct_messages'),

	path('room_membership/<str:username>/<int:room_id>/', views.room_membership, name='room_membership'),
    path('room/<int:room_id>/request/membership/', views.request_room_membership, name='request_room_membership'),
    path('<str:username>/room/<int:room_id>/request/membership/withdraw/', views.withdraw_room_membership_request, name='withdraw_room_membership_request'),
    path('<str:username>/room/<int:room_id>/request/membership/accept/', views.accept_room_membership_request, name='accept_room_membership_request'),

	path('room/<int:pk>/', views.room, name='room'),
	path('checkview/', views.checkview, name='checkview'),
	path('send/', views.send, name='send'),
    path('getMessages/<int:room_id>/', views.getMessages, name='getMessages'),

	path('my/rooms/', views.UserRoomListView.as_view(), name='room-list-by-user'),
	path('rooms/', views.RoomListView.as_view(), name='room-list'),
    path('room/<int:pk>/', views.RoomDetailView.as_view(), name='room-detail'),
	path('rooms/new/', views.RoomCreateView.as_view(), name='room-create'), # Create new post
    path('rooms/update/<int:pk>/', views.RoomUpdateView.as_view(), name='room-update'), # Update specific post (if user on page is same one who created the original post)
    path('rooms/delete/<int:pk>/', views.RoomDeleteView.as_view(), name='room-delete'), # Delete specific post (if user on page is same one who created the original post)

]