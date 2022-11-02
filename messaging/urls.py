from django.urls import path
from . import views


urlpatterns = [
   	path('', views.inbox, name='inbox'),
	path('direct/message/notification/', views.directMessageNotification, name='direct-message-notification'),
	path('user/<int:pk>/', views.detail, name='detail'),
	path('sent/<int:pk>/', views.sentDirectMessage, name='sent_direct_message'),
	path('received/<int:pk>/', views.receivedDirectMessages, name='received_direct_messages'),

	path('rooms/', views.enter_room, name='enter_room'),
	path('room/<int:pk>/', views.room, name='room'),
	path('checkview/', views.checkview, name='checkview'),
	path('send/', views.send, name='send'),
    path('getMessages/<int:room_id>/', views.getMessages, name='getMessages'),

]