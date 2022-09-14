from django.urls import path
from .views import (ListingListView, index)


urlpatterns = [

    path('', index, name='market-index'),
    path('listings/', ListingListView.as_view(), name='listings')

]