from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [

    path('', views.finance_home, name='finance-home'),
    path('query/', views.query, name='query'),

    path('transaction/list/', views.TransactionListView.as_view(), name='transaction-list'), 
    path('transaction/list/<str:username>/', views.UserTransactionListView.as_view(), name='transaction-list-by-user'), # View all transactions by specific user as specified in URL
    path('transaction/new/', views.TransactionCreateView.as_view(), name='transaction-create'),
    path('transaction/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    path('transaction/update/<int:pk>/', views.TransactionUpdateView.as_view(), name='transaction-update'), # Update specific entry (if user on page is same one who created the original entry)
    path('transaction/delete/<int:pk>/', views.TransactionDeleteView.as_view(), name='transaction-delete'), # Delete specific post (if user on page is same one who created the original post)

    path('chain/list/', views.ChainListView.as_view(), name='chain-list'), 
    path('chain/list/<str:username>/', views.UserChainListView.as_view(), name='chain-list-by-user'), # View all transactions by specific user as specified in URL
    path('chain/new/', views.ChainCreateView.as_view(), name='chain-create'),
    path('chain/<int:pk>/', views.ChainDetailView.as_view(), name='chain-detail'),
    path('chain/update/<int:pk>/', views.ChainUpdateView.as_view(), name='chain-update'), # Update specific entry (if user on page is same one who created the original entry)
    path('chain/delete/<int:pk>/', views.ChainDeleteView.as_view(), name='chain-delete'), # Delete specific post (if user on page is same one who created the original post)

    path('entity/list/', views.EntityListView.as_view(), name='entity-list'), 
    path('entity/list/<str:username>/', views.EntityListView.as_view(), name='entity-list-by-user'), # View all transactions by specific user as specified in URL
    path('entity/new/', views.EntityCreateView.as_view(), name='entity-create'),
    path('entity/<int:pk>/', views.EntityDetailView.as_view(), name='entity-detail'),
    path('entity/update/<int:pk>/', views.EntityUpdateView.as_view(), name='entity-update'), # Update specific entry (if user on page is same one who created the original entry)
    path('entity/delete/<int:pk>/', views.EntityDeleteView.as_view(), name='entity-delete'), # Delete specific post (if user on page is same one who created the original post)

    path('theme/list/', views.ThemeListView.as_view(), name='theme-list'), 
    path('theme/list/<str:username>/', views.UserThemeListView.as_view(), name='theme-list-by-user'), # View all transactions by specific user as specified in URL
    path('theme/new/', views.ThemeCreateView.as_view(), name='theme-create'),
    path('theme/<int:pk>/', views.ThemeDetailView.as_view(), name='theme-detail'),
    path('theme/update/<int:pk>/', views.ThemeUpdateView.as_view(), name='theme-update'), # Update specific entry (if user on page is same one who created the original entry)
    path('theme/delete/<int:pk>/', views.ThemeDeleteView.as_view(), name='theme-delete'), # Delete specific post (if user on page is same one who created the original post)

    path('era/list/', views.EraListView.as_view(), name='era-list'), 
    path('era/list/<str:username>/', views.UserEraListView.as_view(), name='era-list-by-user'), # View all transactions by specific user as specified in URL
    path('era/new/', views.EraCreateView.as_view(), name='era-create'),
    path('era/<int:pk>/', views.EraDetailView.as_view(), name='era-detail'),
    path('era/update/<int:pk>/', views.EraUpdateView.as_view(), name='era-update'), # Update specific entry (if user on page is same one who created the original entry)
    path('era/delete/<int:pk>/', views.EraDeleteView.as_view(), name='era-delete'), # Delete specific post (if user on page is same one who created the original post)

]
