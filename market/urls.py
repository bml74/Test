from django.urls import path
from . import views


urlpatterns = [

    path('tickets/', views.ticket_hub_sales, name='ticket_hub'),
    path('tickets/sales/', views.ticket_hub_sales, name='ticket_hub_sales'),
    path('tickets/purchases/', views.ticket_hub_purchases, name='ticket_hub_purchases'),

    path('request/ticket/digitally/transaction/<int:transaction_id>/listing/<int:listing_id>/', views.requestTicketDigitally, name='requestTicketDigitally'),
    path('ticket/portal/transaction/<int:transaction_id>/listing/<int:listing_id>/', views.ticketPortal, name='ticketPortal'),
    path('ticket/portal/transaction/<int:transaction_id>/listing/<int:listing_id>/<str:party>/<str:username>/', views.verify_receipt_of_ticket, name='verify_receipt_of_ticket'),

    path('ticket/create/transaction/<int:transaction_pk>/listing/<int:listing_id>/', views.TicketFileCreateView.as_view(), name='ticket-create'),
    path('ticket/update/transaction/<int:transaction_pk>/listing/<int:listing_id>/file/<int:pk>/', views.TicketFileUpdateView.as_view(), name='ticket-update'),
    path('ticket/delete/transaction/<int:transaction_pk>/listing/<int:listing_id>/file/<int:pk>/', views.TicketFileDeleteView.as_view(), name='ticket-delete'),

    path('ticket/transaction/<int:transaction_pk>/listing/<int:listing_id>/file/<int:pk>/', views.ticketFileDetailView, name='ticket-file-detail'),

    # Listings
    path('listings/<str:filter>/', views.ListingListView.as_view(), name='listings'),
    path('<str:username>/listings/', views.ListingsByUserListView.as_view(), name='listings_by_user'),
    path('listing/<int:pk>/', views.ListingDetailView.as_view(), name='listing'),
    path('listing/update/<int:pk>/', views.ListingUpdateView.as_view(), name='listing-update'),
    path('listing/delete/<int:pk>/', views.ListingDeleteView.as_view(), name='listing-delete'),

    path('listing/create/type/', views.request_or_offer, name='request_or_offer'),

    path('listing/create/<str:listings_type>/', views.ListingCreateView.as_view(), name='listing-create'),

    path('listings/<str:filter>/requests/', views.ListingRequestsToBuyListView.as_view(), name='listings-requests-to-buy'),
    path('switch/<str:obj_type>/<int:pk>/', views.switch_listing, name='listing-request-to-offer'),

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
    path('cancel/delivery/<int:transaction_pk>/<int:suggestion_pk>/', views.cancel_delivery, name='cancel_delivery'),

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

    path('my_purchases/', views.my_purchases, name='my_purchases'),
    path('my_sales/', views.my_sales, name='my_sales'),

    path('request_payments/from/<int:group_id>/listing/<int:listing_for_group_members_id>/', views.request_payment_from_all_group_members, name='request_payment_from_all_group_members'),

    path('request_payment/from/<int:group_id>/to/<int:user_id>/listing/<int:listing_for_group_members_id>/', views.request_payment, name='request_payment'),
    path('reject_payment_request/from/<int:group_id>/to/<int:user_id>/listing/<int:listing_for_group_members_id>/', views.reject_payment_request, name='reject_payment_request'),
    
    path('my/notifications/', views.RequestForPaymentToGroupMemberListView.as_view(), name='notifications'),

    path('create/listing/group/<int:group_id>/', views.ListingForGroupMembersCreateView.as_view(), name='listing-for-group-members-create'),
    path('update/listing/<int:pk>/group/<int:group_id>/', views.ListingForGroupMembersUpdateView.as_view(), name='listing-for-group-members-update'),
    path('delete/listing/<int:pk>/group/<int:group_id>/', views.ListingForGroupMembersDeleteView.as_view(), name='listing-for-group-members-delete'),

    # path('event-attendance/<str:username>/listing_for_group_members/<int:listing_id>/', views.event_attendance, name='event-attendance'),

    path('lottery/<int:pk>/', views.LotteryDetailView.as_view(), name='lottery'),
    path('enter/lottery/<int:lottery_pk>/', views.add_lottery_participant, name='add_lottery_participant'),
    path('lotteries/', views.LotteryListView.as_view(), name='lotteries'),

    path('redirect/from/ad/to/listing/<int:pk>/', views.redirect_from_ad_to_listing, name='redirect_from_ad_to_listing'),

]