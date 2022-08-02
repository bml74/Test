from django.urls import path
from . import views


urlpatterns = [

    path('list/', views.PostListView.as_view(), name='post-list'), 
    path('list/<str:username>/', views.UserPostListView.as_view(), name='post-list-by-user'), # View all post by specific user as specified in URL
    path('new/', views.PostCreateView.as_view(), name='post-create'), # Create new post
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'), # View single post detail 
    path('update/<int:pk>/', views.PostUpdateView.as_view(), name='post-update'), # Update specific post (if user on page is same one who created the original post)
    path('delete/<int:pk>/', views.PostDeleteView.as_view(), name='post-delete'), # Delete specific post (if user on page is same one who created the original post)
    # path('update/<int:pk>/favorite/', views.favorite_post, name='favorite_post'), # favorite an article
    # path('favorites/', views.Favorites.as_view(), name='favorite_list'), # View all favorites

]
