from django.urls import path
from .views import *
from . import views


urlpatterns = [

    path('offers/', views.AdOfferListView.as_view(), name='ad-offers'), 
    path('offer/<int:pk>/', views.AdOfferDetailView.as_view(), name='ad-offer'),  
    path('offer/new/', views.AdOfferCreateView.as_view(), name='ad-offer-create'),
    path('offer/update/<int:pk>/', views.AdOfferUpdateView.as_view(), name='ad-offer-update'),
    path('offer/delete/<int:pk>/', views.AdOfferDeleteView.as_view(), name='ad-offer-delete'),

    path('user/purchases/<str:username>/', views.AdPurchaseByUserListView.as_view(), name='ad-purchases-by-user'), 
    path('group/purchases/<str:group_name>/', views.AdPurchaseByGroupListView.as_view(), name='ad-purchases-by-group'), 
    path('purchase/<int:pk>/', views.AdPurchaseDetailView.as_view(), name='ad-purchase'),  
    path('new/purchase/', views.AdPurchaseCreateView.as_view(), name='ad-purchase-create'),
    path('update/purchase/<int:pk>/', views.AdPurchaseUpdateView.as_view(), name='ad-purchase-update'),
    path('delete/purchase/<int:pk>/', views.AdPurchaseDeleteView.as_view(), name='ad-purchase-delete'),

]