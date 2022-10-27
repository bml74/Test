import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from config.utils import is_ajax
from .models import Map, Event
from .forms import MapForm


def maps_home(request):
    context = {"maps": Map.objects.all()}
    return render(request, "maps_engine/maps_home.html", context)

def maps_query(request):
    if request.method == "GET":
        term = request.GET.get('term', None)
        if term: # If term is not None.
            print(term)
            context = {'term': term}

            results = Map.objects.filter(title__contains=term).all()

            context.update({"results": results})

            return render(request, 'maps_engine/maps_query.html', context)
    return render(request, 'maps_engine/maps_home.html')

def create_map(request):
    if is_ajax(request):
        title = request.GET.get('title') if request.GET.get('title') else None
        description = request.GET.get('description') if request.GET.get('description') else None
        image_url = request.GET.get('image_url') if request.GET.get('image_url') else None
        # FOR DATES:
        # d0 = date(2008, 8, 18)
        # d1 = date(2008, 9, 26)
        # delta = d1 - d0.
        # print(delta. days)

        # num_days_since (both) and day_of_week should be automatic with datetime

        print(f"""
        TITLE: {title}
        DESCRIPTION: {description}
        IMAGE URL: {image_url}
        """)
    return render(request, 'maps_engine/create_map.html')

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


class MapListView(UserPassesTestMixin, ListView):
    model = Map
    template_name = 'market/Maps.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(MapListView, self).get_context_data(**kwargs)
        num_results = len(Map.objects.all())
        context.update({
            "num_results": num_results
        })
        return context

    def get_queryset(self):
        return Map.objects.order_by('-title')


class MapDetailView(UserPassesTestMixin, DetailView):
    model = Map

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        map = get_object_or_404(Map, pk=kwargs['pk'])

        context = {
            "item": map, 
        }

        return render(request, 'market/map.html', context)


class MapCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Map
    fields = ['title', 'description', 'image_url']
    template_name = 'maps_engine/create_map.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(MapCreateView, self).get_context_data(**kwargs)
        header = "Create map"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class MapUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Map
    fields = ['title', 'description', 'image_url']
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().creator

    def get_context_data(self, **kwargs):
        context = super(MapUpdateView, self).get_context_data(**kwargs)
        header = "Update map"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class MapDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete Map."""
    model = Map
    success_url = '/maps/'
    context_object_name = 'item'
    template_name = 'market/confirm_delete.html'

    def test_func(self):
        return self.request.user == self.get_object().creator

    def get_context_data(self, **kwargs):
        context = super(MapDeleteView, self).get_context_data(**kwargs)
        transaction = get_object_or_404(Map, id=self.kwargs.get('pk'))
        title = f"Map: {transaction.title}"
        context.update({"type": "map", "title": title})
        return context


class EventListView(UserPassesTestMixin, ListView):
    model = Event
    template_name = 'market/Events.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        num_results = len(Event.objects.all())
        context.update({
            "num_results": num_results
        })
        return context

    def get_queryset(self):
        return Event.objects.order_by('-title')


class EventDetailView(UserPassesTestMixin, DetailView):
    model = Event

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        Event = get_object_or_404(Event, pk=kwargs['pk'])

        context = {
            "item": Event, 
            "user_is_creator": Event.creator == request.user
        }

        return render(request, 'market/event.html', context)


class EventCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Event
    fields = ['title', 'description', 'price', 'date_due', 'visibility', 'Event_category', 'non_fungible_order', 'quantity_available', 'Event_medium']
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(EventCreateView, self).get_context_data(**kwargs)
        header = "Create event"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    fields = ['title', 'description', 'price', 'date_due', 'visibility', 'Event_category', 'non_fungible_order', 'quantity_available', 'Event_medium']
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().creator

    def get_context_data(self, **kwargs):
        context = super(EventUpdateView, self).get_context_data(**kwargs)
        header = "Update event"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    success_url = '/maps/'
    context_object_name = 'item'
    template_name = 'market/confirm_delete.html'

    def test_func(self):
        return self.request.user == self.get_object().creator

    def get_context_data(self, **kwargs):
        context = super(EventDeleteView, self).get_context_data(**kwargs)
        transaction = get_object_or_404(Event, id=self.kwargs.get('pk'))
        title = f"Event: {transaction.title}"
        context.update({"type": "event", "title": title})
        return context



# Function for create_map 
# Rather than being a view make it a function. When you click save map, send map data and save all that. Also send all events data and save all that.


# @login_required
# def map_create(request):
#     if request.method == 'POST':
#         print(request.POST, request.FILES)
#         form = MapForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('map-create-test')
#     else:
#         form = MapForm()
#     context = {'form': form}
#     return render(request, 'market/dashboard/form_view.html', context=context)


def process_map_data(df):
    print(df.columns)
    print(df.shape)
    print(df.head(15))
    print("First row:")
    print(df.iloc[0])
    # Delete row if there is no latitude or longitude:
    df = df[pd.notnull(df['latitude'])]
    df = df[pd.notnull(df['longitude'])]
    for index, row in df.iterrows():
        latitude = row.get('latitude'); longitude = row.get('longitude'); altitude = row.get('altitude'); geometry = row.get('geometry')
        primary_city_name = row.get('primary_city_name'); alternative_city_names = row.get('alternative_city_names')
        primary_region_name = row.get('primary_region_name'); alternative_region_names = row.get('alternative_region_names')
        primary_country_name = row.get('primary_country_name'); alternative_country_names = row.get('alternative_country_names')
        address = row.get('address'); postcode = row.get('postcode'); district = row.get('district'); neighborhood = row.get('neighborhood')
        number_of_days_after_anchor_date_that_event_began=int(row.get('number_of_days_after_anchor_date_that_event_began', 0))
        number_of_days_after_anchor_date_that_event_ended=int(row.get('number_of_days_after_anchor_date_that_event_ended', 0))
        start_date = row.get('start_date'); end_date = row.get('end_date')
        title = row.get('title') if row.get('title') is not None else row.get('primary_city_name', '')
        description = row.get('description', '')
        link = row.get('link', '')
        marker_color = row.get('marker_color') if row.get('marker_color') else 'blue'
        content_online = row.get('content_online', 0)
        number_of_sites = row.get('number_of_sites', 0)
        number_of_casualties = row.get('number_of_casualties', 0)
        alternative_id = row.get('alternative_id')
        number_of_memorials = row.get('number_of_memorials')
        type_of_place_before_event = row.get('type_of_place_before_event')
        occupation_period = row.get('occupation_period')

        print(f"latitude: {latitude}")
        print(f"longitude: {longitude}")
        print(f"altitude: {altitude}")
        print(f"geometry: {geometry}")
        print(f"primary_city_name: {primary_city_name}")
        print(f"alternative_city_names: {alternative_city_names}")
        print(f"primary_region_name: {primary_region_name}")
        print(f"alternative_region_names: {alternative_region_names}")
        print(f"primary_country_name: {primary_country_name}")
        print(f"alternative_country_names: {alternative_country_names}")
        print(f"address: {address}")
        print(f"postcode: {postcode}")
        print(f"district: {district}")
        print(f"neighborhood: {neighborhood}")
        print(f"number_of_days_after_anchor_date_that_event_began: {number_of_days_after_anchor_date_that_event_began}")
        print(f"number_of_days_after_anchor_date_that_event_ended: {number_of_days_after_anchor_date_that_event_ended}")
        print(f"start_date: {start_date}")
        print(f"end_date: {end_date}")
        print(f"title: {title}")
        print(f"description: {description}")
        print(f"link: {link}")
        print(f"marker_color: {marker_color}")
        print(f"content_online: {content_online}")
        print(f"number_of_sites: {number_of_sites}")
        print(f"number_of_casualties: {number_of_casualties}")
        print(f"alternative_id: {alternative_id}")
        print(f"number_of_memorials: {number_of_memorials}")
        print(f"type_of_place_before_event: {type_of_place_before_event}")
        print(f"occupation_period: {occupation_period}")

        e = Event(
            latitude=row.get('latitude'), longitude=row.get('longitude'), altitude=row.get('altitude'), geometry=row.get('geometry'), 
            primary_city_name=row.get('primary_city_name'), alternative_city_names=row.get('alternative_city_names'),
            primary_region_name=row.get('primary_region_name'), alternative_region_names=row.get('alternative_region_names'),
            primary_country_name=row.get('primary_country_name'), alternative_country_names=row.get('alternative_country_names'),
            address=row.get('address'), postcode=row.get('postcode'), district=row.get('district'), neighborhood=row.get('neighborhood'),
            number_of_days_after_anchor_date_that_event_began=int(row.get('number_of_days_after_anchor_date_that_event_began', 0)), 
            number_of_days_after_anchor_date_that_event_ended=int(row.get('number_of_days_after_anchor_date_that_event_ended', 0)),
            start_date=row.get('start_date'), end_date=row.get('end_date'),
            title=row.get('title') if row.get('title') is not None else row.get('primary_city_name', ''),
            description=row.get('description', ''),
            link=row.get('link', ''),
            marker_color=row.get('marker_color') if row.get('marker_color') else 'blue',
            content_online=row.get('content_online', 0),
            number_of_sites=row.get('number_of_sites', 0),
            number_of_casualties=row.get('number_of_casualties', 0),
            alternative_id=row.get('alternative_id'),
            number_of_memorials=row.get('number_of_memorials'),
            type_of_place_before_event=row.get('type_of_place_before_event'),
            occupation_period=row.get('occupation_period')
        )
        e.save()

    print(df.head())


class MapCreateTestView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Map
    fields = ['title', 'description', 'anchor_date', 'image_url', 'excel_upload']
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        FILE = form.instance.excel_upload # Get the file
        FILE_NAME = FILE.name # Get the file name
        print(f"FILE_NAME: {FILE_NAME}") # ex. yahad.xlsx
        FILE_EXTENSION = FILE_NAME.split(".")[-1]
        if FILE_EXTENSION == "csv":
            df = pd.read_csv(FILE) 
        elif FILE_EXTENSION == "xlsx" or FILE_EXTENSION == "xls":
            df = pd.read_excel(FILE) 
        process_map_data(df)
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(MapCreateTestView, self).get_context_data(**kwargs)
        context['header'] = "Create map"
        context['create'] = True
        return context


