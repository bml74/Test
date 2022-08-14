"""malagosto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from . import views
from users import views as user_views

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('ajax-chatbox/', views.ajax_chatbox, name='ajax-chatbox'),
    path('docs/chatbox/', views.chatbox_docs, name='chatbox_docs'),

    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('profile/', user_views.profile, name='profile'),
    path('profile/<str:username>/', user_views.user_profile, name='user_profile'),

    path('posts/', include('posts.urls')),
    path('écoles/', include('ecoles.urls')), path('ecoles/', include('ecoles.urls')),
    path('news/', include('news.urls')), 
    path('newsfeed/', include('newsfeed.urls')), 
    path('maps/', include('maps.urls')), 
    path('messaging/', include('messaging.urls')), 
    path('data/', include('data.urls')), 

    path('finance/', include('finance.urls')),

    


]
