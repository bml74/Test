from django.urls import path
from .views import (
    ListingListView, 
    ListingDetailView, 
    ListingCreateView, 
    ListingUpdateView, 
    ListingDeleteView, 
    checkout,
    payment_success,
    payment_cancel,
    learning_carousel,
    my_listings
)


urlpatterns = [

    path('listings/', ListingListView.as_view(), name='listings'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing'),
    path('listings/create/', ListingCreateView.as_view(), name='listing-create'),
    path('listings/update/<int:pk>/', ListingUpdateView.as_view(), name='listing-update'),
    path('listings/delete/<int:pk>/', ListingDeleteView.as_view(), name='listing-delete'),

    path('lc/', learning_carousel, name='learning_carousel'),

    path('my/listings/', my_listings, name='my_listings'),

    path('checkout/<int:pk>/', checkout, name='checkout'),
    path('checkout/success/', payment_success, name='payment_success'),
    path('checkout/cancel/', payment_cancel, name='payment_cancel')

]