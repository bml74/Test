from django.shortcuts import render


def maps_home(request):
    return render(request, "maps_engine/maps_home.html")

def mapbox_terrain(request):
    return render(request, "maps_engine/mapboxjs/terrain.html")

def mapbox_directions(request):
    return render(request, "maps_engine/mapboxjs/directions.html")

def mapbox_geocoder(request):
    return render(request, "maps_engine/mapboxjs/geocoder.html")

def mapbox_marker_from_geocode(request):
    return render(request, "maps_engine/mapboxjs/marker_from_geocode.html")

def mapbox_airports(request):
    return render(request, "maps_engine/mapboxjs/mapbox_airports.html")

def yahad_map(request):
    return render(request, "maps_engine/mapboxjs/YAHADMAP.html")

def google_map(request):
    return render(request, "maps_engine/googlemaps/google_map.html")
