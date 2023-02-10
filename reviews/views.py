from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.models import User, Group
from orgs.models import GroupProfile
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Review, CustomerMessage
from ecoles.datatools import generate_recommendations_from_queryset
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME
from config.utils import formValid, getOverallRating, myround
from config.abstract_settings.model_fields import (
    REVIEW_FIELDS
)
from users.models import Rating
from config.abstract_settings import VARIABLES


class ReviewOfUserListView(ListView):

    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'items'
    paginate_by = VARIABLES.PAGINATE_BY

    def get_queryset(self):
        """Get posts by specific user (as passed into URL)."""
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Review.objects.filter(subject=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super(ReviewOfUserListView, self).get_context_data(**kwargs)
        username = self.kwargs.get('username')
        subject = get_object_or_404(User, username=username)
        overall_rating = getOverallRating(subject)
        overall_rating *= 20
        starClass = myround(x=overall_rating, base=10)
        context.update({"header": f"Reviews of {username}", "subject": subject, "starClass": starClass})
        return context


class ReviewDetailView(UserPassesTestMixin, DetailView):
    model = Review
    template_name = 'reviews/review_detail.html'
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(ReviewDetailView, self).get_context_data(**kwargs)
        review = get_object_or_404(Review, id=self.kwargs['pk'])
        return context


class ReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Review
    fields = REVIEW_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        subject_username = self.kwargs.get('username')
        subject = get_object_or_404(User, username=subject_username)
        form.instance.subject = subject
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(ReviewCreateView, self).get_context_data(**kwargs)
        subject_username = self.kwargs.get('username')
        header = f"Add review of {subject_username}"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = REVIEW_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        subject_username = self.kwargs.get('username')
        subject = get_object_or_404(User, username=subject_username)
        form.instance.subject = subject
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(ReviewUpdateView, self).get_context_data(**kwargs)
        subject_username = self.kwargs.get('username')
        header = f"Update review of {subject_username}"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete post."""
    model = Review
    success_url = '/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(ReviewDeleteView, self).get_context_data(**kwargs)
        transaction = get_object_or_404(Review, id=self.kwargs.get('pk'))
        title = f"Review: {transaction.title}"
        context.update({"type": "review", "title": title})
        return context


class CustomerMessageListView(UserPassesTestMixin, ListView):
    model = CustomerMessage
    template_name = 'reviews/customer-messages.html'
    context_object_name = 'items'
    paginate_by = VARIABLES.PAGINATE_BY

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(CustomerMessageListView, self).get_context_data(**kwargs)
        context.update({"header": "Feedback"})
        return context


class CustomerMessageDetailView(UserPassesTestMixin, DetailView):
    model = CustomerMessage
    template_name = 'reviews/customer-message.html'

    def test_func(self):
        return self.request.user.is_superuser 

    def get_context_data(self, **kwargs):
        context = super(CustomerMessageDetailView, self).get_context_data(**kwargs)
        customerMessage = get_object_or_404(CustomerMessage, id=self.kwargs['pk'])
        context = {"header": f"Feedback from {customerMessage.author}", "item": customerMessage}
        return context


class CustomerMessageCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CustomerMessage
    fields = ['title', 'content']
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(CustomerMessageCreateView, self).get_context_data(**kwargs)
        header = "Create review"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context

