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
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction'),

    # Payments
    path('checkout/<str:obj_type>/<int:pk>/', views.checkout, name='checkout'),
    path('checkout_session/<str:obj_type>/<int:pk>/',views.checkout_session,name='checkout_session'),
    path('checkout/success/<str:obj_type>/', views.payment_success, name='payment_success'),
    path('checkout/cancel/', views.payment_cancel, name='payment_cancel'),
    #getting all unverified payments of purchaser
    path('my_payments/', views.my_payments, name='my_payments'),
    #updating unverified payments of purchaser
    path('confirm_transaction/<int:transaction_id>/', views.confirm_transaction, name='confirm_transaction'),
    path('reject_transaction/<int:transaction_id>/', views.reject_transaction, name='reject_transaction'),

    # path('checkout/<int:pk>/', views.item_checkout, name='item_checkout'),
    # path('checkout_session/<int:id>/',views.item_checkout_session,name='item_checkout_session'),
    # path('checkout/success/', views.payment_success, name='payment_success'),
    # path('checkout/cancel/', views.payment_cancel, name='payment_cancel'),

]