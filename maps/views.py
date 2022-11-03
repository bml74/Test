import pandas as pd
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from config.utils import is_ajax, get_as_df
from .models import Map, Event
from .forms import MapForm
from config.utils import download_file
from django.http import HttpResponse, JsonResponse
from .utils import db_model_to_geojson, get_geojson_in_dict_form_from_model, process_map_data
from pprint import pprint
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME


@staff_member_required
def maps_admin_panel(request):
    return render(request, 'maps_engine/maps_admin_panel.html')


@staff_member_required
def export_maps_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    data = download_file(request, queryset=Map.objects.all(), CONTENT_TYPE='text', FILE_TYPE='csv', FILE_EXTENSION='csv')
    response = HttpResponse(data, content_type='text/csv')
    return response


@login_required # ALso make sure user created map
def get_events_as_geojson(request, pk):
    map_obj = get_object_or_404(Map, pk=pk)
    events = Event.objects.filter(parent_map=map_obj).all()
    data = db_model_to_geojson(queryset=events)
    response = HttpResponse(data, content_type='application/json')
    return response


@staff_member_required
def export_events_csv(request, pk):
    map_obj = get_object_or_404(Map, pk=pk)
    events = Event.objects.filter(parent_map=map_obj).all()
    data = download_file(request, queryset=events, CONTENT_TYPE='text', FILE_TYPE='csv', FILE_EXTENSION='csv')
    response = HttpResponse(data, content_type='text/csv')
    return response


def viewEventsInTableInBrowser(request, pk):
    map_obj = get_object_or_404(Map, pk=pk)
    events = Event.objects.filter(parent_map=map_obj).all()
    print(events)
    print()
    print(len(events))
    df = get_as_df(queryset=events)
    print(df)
    # Manipulate DataFrame using to_html() function
    table = df.to_html()
    return HttpResponse(table)



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
        # image_url = request.GET.get('image_url') if request.GET.get('image_url') else None
        # FOR DATES:
        # d0 = date(2008, 8, 18)
        # d1 = date(2008, 9, 26)
        # delta = d1 - d0.
        # print(delta. days)

        # num_days_since (both) and day_of_week should be automatic with datetime

        print(f"""
        TITLE: {title}
        DESCRIPTION: {description}
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
        map_obj = get_object_or_404(Map, pk=kwargs['pk'])
        events = Event.objects.filter(parent_map=map_obj).all()
        event_data_dict =  get_geojson_in_dict_form_from_model(queryset=events)
        GEOJSON = json.dumps(event_data_dict["features"]) 
        pprint(GEOJSON)
        print(len(event_data_dict["features"]))
        print()
        pprint(event_data_dict["features"][0])
        context = {
            "item": map_obj, 
        }
        return render(request, 'market/map.html', context)


def get_geojson_data_for_js(request, pk):
    map_obj = get_object_or_404(Map, pk=pk)
    events = Event.objects.filter(parent_map=map_obj).all()
    my_dict = get_geojson_in_dict_form_from_model(events)
    geojson = json.dumps(my_dict["features"][0])
    return JsonResponse(geojson, safe=False)

class MapRenderDetailView(UserPassesTestMixin, DetailView):
    model = Map

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        map_obj = get_object_or_404(Map, pk=kwargs['pk'])
        events = Event.objects.filter(parent_map=map_obj).all()
        event_data_dict =  get_geojson_in_dict_form_from_model(queryset=events)
        GEOJSON = json.dumps(event_data_dict) 
        pprint(GEOJSON)
        print(len(event_data_dict["features"]))
        print()
        pprint(event_data_dict["features"][0])
        context = {
            "item": map_obj, 
            "GEOJSON": GEOJSON,
            "events": events
        }
        return render(request, 'maps_engine/mapboxjs/map_detail.html', context)


class MapManualCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Map
    fields = ['title', 'description', 'map_image']
    template_name = 'maps_engine/create_map.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(MapManualCreateView, self).get_context_data(**kwargs)
        header = "Create map"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class MapUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Map
    fields = ['title', 'description', 'map_image']
    template_name = FORM_VIEW_TEMPLATE_NAME

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
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

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
    template_name = FORM_VIEW_TEMPLATE_NAME

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
    template_name = FORM_VIEW_TEMPLATE_NAME

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
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

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
#             return redirect('map-create-via-import')
#     else:
#         form = MapForm()
#     context = {'form': form}
#     return render(request, FORM_VIEW_TEMPLATE_NAME, context=context)


class MapCreateViaImportView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Map
    fields = ['title', 'description', 'anchor_date', 'map_image', 'excel_upload']
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form, **kwargs):
        FILE = form.instance.excel_upload # Get the file

        print(f"OBJECT: {self.object}")
        print(f"OBJECT TYPE: {type(self.object)}")
        if FILE:
            FILE_NAME = FILE.name # Get the file name
            print(f"FILE_NAME: {FILE_NAME}") # ex. yahad.xlsx
            FILE_EXTENSION = FILE_NAME.split(".")[-1]
            if FILE_EXTENSION == "csv":
                df = pd.read_csv(FILE) 
            elif FILE_EXTENSION == "xlsx" or FILE_EXTENSION == "xls":
                df = pd.read_excel(FILE) 
            self.object = form.save() # Get Map object
            process_map_data(df, parent_map=self.object)
        self.object = form.save() # Get Map object
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(MapCreateViaImportView, self).get_context_data(**kwargs)
        context['header'] = "Create map"
        context['create'] = True
        return context

