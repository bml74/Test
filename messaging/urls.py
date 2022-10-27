from django.urls import path
from . import views


urlpatterns = [
   	path('', views.inbox, name='inbox'),
	path('direct/message/notification/', views.directMessageNotification, name='direct-message-notification'),
	path('user/<int:pk>/', views.detail, name='detail'),
	path('sent/<int:pk>/', views.sentDirectMessage, name='sent_direct_message'),
	path('received/<int:pk>/', views.receivedDirectMessages, name='received_direct_messages'),
]