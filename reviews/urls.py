from django.urls import path
from . import views


urlpatterns = [

    path('subject/<str:username>/', views.ReviewOfUserListView.as_view(), name='review-list'), 
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'), 
    path('new/of/<str:username>/', views.ReviewCreateView.as_view(), name='review-create'), 
    path('update/of/<str:username>/<int:pk>/', views.ReviewUpdateView.as_view(), name='review-update'),
    path('delete/<int:pk>/', views.ReviewDeleteView.as_view(), name='review-delete'), 

]
