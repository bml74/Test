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
from two_factor.urls import urlpatterns as tf_urls
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('search/results/', views.search_results, name='search-results'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path('ajax-chatbox/', views.ajax_chatbox, name='ajax-chatbox'),
    path('docs/chatbox/', views.chatbox_docs, name='chatbox_docs'),

    path('register/', user_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('', include(tf_urls)),
    path('profile/', user_views.profile, name='profile'),
    path('profile/connect-to-stripe', user_views.profileConnectToStripe, name='profile_connect_to_stripe'),
    path('profile/stripe-connect-callback/<str:stripe_account_id>/', user_views.profileStripeConnectCallback, name='stripe_connect_callback'),
    path('referral/', user_views.referral, name='referral'),
    path('profile/<str:username>/', user_views.user_profile, name='user_profile'),

    path('users/', include('users.urls')),
    path('groups/', include('orgs.urls')),
    path('ads/', include('ads.urls')),
    path('posts/', include('posts.urls')),
    path('écoles/', include('ecoles.urls')), path('ecoles/', include('ecoles.urls')),
    path('news/', include('news.urls')), 
    path('feeds/', include('newsfeed.urls')), 
    path('maps/', include('maps.urls')), 
    path('messaging/', include('messaging.urls')), 
    path('data/', include('data.urls')), 
    path('quizzes/', include('quizzes.urls')), 
    path('market/', include('market.urls')), 

    path('finance/', include('finance.urls')),


    path('asdf/', views.vue_example, name='vue_example'),

]
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404="config.views.error_404_view"
