from django.urls import path
from . import views


urlpatterns = [
    path('', views.maps_home, name='maps_home'),
    path('query/', views.maps_query, name='maps_query'),
    path('mapbox/terrain/', views.mapbox_terrain, name='mapbox_terrain'),
    path('mapbox/directions/', views.mapbox_directions, name='mapbox_directions'),
    path('mapbox/geocoder/', views.mapbox_geocoder, name='mapbox_geocoder'), 
    path('mapbox/marker/', views.mapbox_marker_from_geocode, name='mapbox_marker_from_geocode'),
    path('mapbox/airports/', views.mapbox_airports, name='mapbox_airports'), 
    path('yahad/', views.yahad_map, name='yahad_map'), 
    path('google/map/', views.google_map, name='google_map'),
]