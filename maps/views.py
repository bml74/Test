from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from .models import Map, Event



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
        Map = get_object_or_404(Map, pk=kwargs['pk'])

        context = {
            "item": Map, 
            "user_is_creator": Map.creator == request.user
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

