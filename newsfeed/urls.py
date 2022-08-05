from django.urls import path
from . import views


urlpatterns = [
    path('', views.feed_home, name='feed-home'),
    path('<int:pk>/', views.single_feed, name='single_feed'),
    path('detail/<int:pk>/', views.FeedDetailView.as_view(), name='feed-detail'),
    path('new/', views.FeedCreateView.as_view(), name='feed-add'),
    path('update/<int:pk>/', views.FeedUpdateView.as_view(), name='feed-update'),
]