from django.urls import path
from . import views


urlpatterns = [

    # Listings
    path('listings/', views.ListingListView.as_view(), name='listings'),
    path('<str:username>/listings/', views.ListingsByUserListView.as_view(), name='listings_by_user'),
    path('listing/<int:pk>/', views.ListingDetailView.as_view(), name='listing'),
    path('listing/create/', views.ListingCreateView.as_view(), name='listing-create'),
    path('listing/update/<int:pk>/', views.ListingUpdateView.as_view(), name='listing-update'),
    path('listing/delete/<int:pk>/', views.ListingDeleteView.as_view(), name='listing-delete'),

    path('groups/listing/<int:pk>/', views.ListingForGroupMembersDetailView.as_view(), name='listing-for-group-members-detail'),

    path('lc/', views.learning_carousel, name='learning_carousel'),

    # Admin
    path('dashboard/', views.dashboard, name='user-dashboard'),
    path('all/transactions/', views.transactions_admin, name='transactions-admin'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction'),

    path('delivery/<int:transaction_pk>/', views.TransactionDeliveryDetailView.as_view(), name='transaction-delivery'),
    path('create/delivery/<int:transaction_pk>/', views.TransactionDeliveryCreateView.as_view(), name='create-delivery-suggestion'),
    # path('listing/update/<int:pk>/', views.TransactionDeliveryUpdateView.as_view(), name='update-delivery-suggestion'),
    # path('listing/delete/<int:pk>/', views.TransactionDeliveryDeleteView.as_view(), name='delete-delivery-suggestion'),

    path('set/delivery/<int:transaction_pk>/<int:suggestion_pk>/', views.set_delivery, name='set_delivery'),

    # Payments
    path('purchase_item_for_free/<str:obj_type>/<int:pk>/', views.purchase_item_for_free, name='purchase_item_for_free'),

    path('checkout/<str:obj_type>/<int:pk>/', views.checkout, name='checkout'),
    path('checkout_session/<str:obj_type>/<int:pk>/',views.checkout_session,name='checkout_session'),
    path('success/checkout/<str:obj_type>/<int:pk>/', views.payment_success, name='payment_success'),
    path('cancel/checkout/', views.payment_cancel, name='payment_cancel'),
    #getting all unverified payments of purchaser
    path('my_payments/', views.my_payments, name='my_payments'),
    #updating unverified payments of purchaser
    path('confirm_transaction/<int:transaction_id>/', views.confirm_transaction, name='confirm_transaction'),
    path('reject_transaction/<int:transaction_id>/', views.reject_transaction, name='reject_transaction'),

    path('connect/stripe/', views.connect_to_stripe_page, name='connect-to-stripe-page'),

    path('my_purchases/', views.my_purchases, name='my_purchases'),
    path('my_sales/', views.my_sales, name='my_sales'),

    path('request_payment/from/<int:group_id>/to/<int:user_id>/listing/<int:listing_for_group_members_id>/', views.request_payment, name='request_payment'),
    path('reject_payment_request/from/<int:group_id>/to/<int:user_id>/listing/<int:listing_for_group_members_id>/', views.reject_payment_request, name='reject_payment_request'),
    
    path('my/payment_requests/', views.RequestForPaymentToGroupMemberListView.as_view(), name='payment_requests'),

    path('create/listing/group/<int:group_id>/', views.ListingForGroupMembersCreateView.as_view(), name='listing-for-group-members-create'),
    path('update/listing/<int:pk>/group/<int:group_id>/', views.ListingForGroupMembersUpdateView.as_view(), name='listing-for-group-members-update'),
    path('delete/listing/<int:pk>/group/<int:group_id>/', views.ListingForGroupMembersDeleteView.as_view(), name='listing-for-group-members-delete'),

    # path('event-attendance/<str:username>/listing_for_group_members/<int:listing_id>/', views.event_attendance, name='event-attendance'),

]