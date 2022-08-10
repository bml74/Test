from django.shortcuts import render
from .models import MapMeta


def maps_home(request):
    context = {"maps": MapMeta.objects.all()}
    return render(request, "maps_engine/maps_home.html", context)

def maps_query(request):
    if request.method == "GET":
        term = request.GET.get('term', None)
        if term: # If term is not None.
            context = {'term': term}

            results = MapMeta.objects.filter(title__contains=term).all()

            context.update({"results": results})

            return render(request, 'maps_engine/maps_query.html', context)
    return render(request, 'maps_engine/maps_home.html')

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
