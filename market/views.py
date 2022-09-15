from django.shortcuts import render

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from .models import Listing
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def index(request):
    return render(request, "market/COURSE_DESIGN.html")


class ListingListView(UserPassesTestMixin, ListView):
    model = Listing
    template_name = 'market/listings.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(ListingListView, self).get_context_data(**kwargs)
        num_results = len(Listing.objects.all())
        context.update({
            "num_results": num_results
        })
        return context

    def get_queryset(self):
        return Listing.objects.order_by('-title')


class ListingDetailView(UserPassesTestMixin, DetailView):
    model = Listing

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        project = get_object_or_404(Listing, pk=kwargs['pk'])

        context = {
            "item": project, 
        }

        return render(request, 'market/listing.html', context)
