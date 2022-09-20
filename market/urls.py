from django.urls import path
from . import views


urlpatterns = [

    # Listings
    path('listings/', views.ListingListView.as_view(), name='listings'),
    path('listings/<int:pk>/', views.ListingDetailView.as_view(), name='listing'),
    path('listings/create/', views.ListingCreateView.as_view(), name='listing-create'),
    path('listings/update/<int:pk>/', views.ListingUpdateView.as_view(), name='listing-update'),
    path('listings/delete/<int:pk>/', views.ListingDeleteView.as_view(), name='listing-delete'),

    path('lc/', views.learning_carousel, name='learning_carousel'),

    # Admin
    path('dashboard/', views.dashboard, name='user-dashboard'),
    path('my/listings/', views.my_listings, name='my_listings'),
    path('all/transactions/', views.transactions_admin, name='transactions-admin'),

    # Payments
    path('checkout/<int:pk>/', views.checkout, name='checkout'),
    path('checkout/success/', views.payment_success, name='payment_success'),
    path('checkout/cancel/', views.payment_cancel, name='payment_cancel')

]