from django.urls import path
from .views import (ListingListView, ListingDetailView, index)


urlpatterns = [

    path('', index, name='market-index'),
    path('listings/', ListingListView.as_view(), name='listings'),
    path('listings/<int:pk>/', ListingDetailView.as_view(), name='listing')

]