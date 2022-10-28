from django.urls import path
from . import views


urlpatterns = [
    path('', views.maps_home, name='maps_home'),
    path('query/', views.maps_query, name='maps_query'),

    path('maps_admin_panel/', views.maps_admin_panel, name='maps_admin_panel'),
    path('export_maps_csv/', views.export_maps_csv, name='export_maps_csv'),

    path('all/', views.MapListView.as_view(), name='maps'),
    path('<int:pk>/', views.MapDetailView.as_view(), name='map'),
    path('<int:pk>/geojson/', views.get_events_as_geojson, name='get_events_as_geojson'),
    path('<int:pk>/export_events_csv/', views.export_events_csv, name='export_events_csv'),
    path('<int:pk>/events/dataframe/', views.viewEventsInTableInBrowser, name='events-table'),
    path('create/', views.create_map, name='map-create'),
    path('update/<int:pk>/', views.MapUpdateView.as_view(), name='map-update'),
    path('delete/<int:pk>/', views.MapDeleteView.as_view(), name='map-delete'),

    path('import/create/', views.MapCreateViaImportView.as_view(), name='map-create-via-import'),

    path('events/', views.EventListView.as_view(), name='events'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event'),
    path('events/create/', views.EventCreateView.as_view(), name='event-create'),
    path('events/update/<int:pk>/', views.EventUpdateView.as_view(), name='event-update'),
    path('events/delete/<int:pk>/', views.EventDeleteView.as_view(), name='event-delete'),



    path('mapbox/terrain/', views.mapbox_terrain, name='mapbox_terrain'),
    path('mapbox/directions/', views.mapbox_directions, name='mapbox_directions'),
    path('mapbox/geocoder/', views.mapbox_geocoder, name='mapbox_geocoder'), 
    path('mapbox/marker/', views.mapbox_marker_from_geocode, name='mapbox_marker_from_geocode'),
    path('mapbox/airports/', views.mapbox_airports, name='mapbox_airports'), 
    path('yahad/', views.yahad_map, name='yahad_map'), 
    path('google/map/', views.google_map, name='google_map'),
]