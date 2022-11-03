from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from .models import AdOffer, AdPurchase
from orgs.models import GroupProfile
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from config.abstract_settings.model_fields import AD_OFFER_FIELDS, AD_PURCHASE_FIELDS
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME


class AdOfferListView(ListView):
    model = AdOffer
    template_name = 'ads/ad_offers.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(AdOfferListView, self).get_context_data(**kwargs)
        context.update({"header": "Ad Offers"})
        return context


class AdOfferDetailView(UserPassesTestMixin, DetailView):
    model = AdOffer
    template_name = 'ads/ad_offer.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super(AdOfferDetailView, self).get_context_data(**kwargs)
        context.update({"header": "Ad Offer"})
        return context

    def test_func(self):
        return self.request.user.is_authenticated


class AdOfferCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AdOffer
    fields = AD_OFFER_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(AdOfferCreateView, self).get_context_data(**kwargs)
        header = "Create ad offer"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class AdOfferUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AdOffer
    fields = AD_OFFER_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(AdOfferUpdateView, self).get_context_data(**kwargs)
        header = "Update ad offer"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class AdOfferDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AdOffer
    success_url = '/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(AdOfferDeleteView, self).get_context_data(**kwargs)
        item = get_object_or_404(AdOffer, id=self.kwargs.get('pk'))
        title = f"Ad offer: {item.title}"
        context.update({"type": "ad offer", "title": title})
        return context


class AdPurchaseByUserListView(ListView):
    model = AdPurchase
    template_name = 'ads/ad_purchases.html'
    context_object_name = 'items'
    paginate_by = 10

    def test_func(self):
        return self.kwargs.get('username') == self.request.user.username

    def get_context_data(self, **kwargs):
        context = super(AdPurchaseByUserListView, self).get_context_data(**kwargs)
        context.update({"header": "Ad purchases by user"})
        return context

    def get_queryset(self):
        return AdPurchase.objects.filter(user_that_purchased_ad=self.request.user).order_by('-date_created').all()


class AdPurchaseByGroupListView(ListView):
    model = AdPurchase
    template_name = 'ads/ad_purchases.html'
    context_object_name = 'items'
    paginate_by = 10

    def test_func(self):
        # Is user member of group? Or is user creator of group?
        group_that_purchased_ad = self.kwargs.get('group_name')
        group_profile = get_object_or_404(GroupProfile, group=group_that_purchased_ad)
        user_in_group = self.request.user.groups.filter(name=group_that_purchased_ad.name).exists() or self.request.user in group_profile.group_members.all()
        user_created_group = self.request.user == group_profile.group_creator
        return user_in_group or user_created_group

    def get_context_data(self, **kwargs):
        context = super(AdPurchaseByGroupListView, self).get_context_data(**kwargs)
        context.update({"header": "Ad purchases by group"})
        return context

    def get_queryset(self, **kwargs):
        return AdPurchase.objects.filter(group_that_purchased_ad=self.kwargs.get('group_name')).order_by('-date_created').all()


class AdPurchaseDetailView(UserPassesTestMixin, DetailView):
    model = AdPurchase
    template_name = 'ads/ad_purchase.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super(AdPurchaseDetailView, self).get_context_data(**kwargs)
        context.update({"header": "Ad purchase"})
        return context

    def test_func(self):
        # If user created ad or user is a member or creator of the group that created the ad
        user = self.request.user # Get user
        ad = get_object_or_404(AdPurchase, id=self.kwargs.get('pk')) # Get AdPurchase object
        user_created_ad = ad.user_that_purchased_ad == user # Boolean: Did the current user create this AdPurchase object?

        group_that_purchased_ad = ad.group_that_purchased_ad # Get Group object of group that purchased ad
        group_profile_of_group_that_purchased_ad = get_object_or_404(GroupProfile, group=group_that_purchased_ad) # Get GroupProfile object
        user_created_group_that_created_ad = user == group_profile_of_group_that_purchased_ad.group_creator # Boolean: Did user create the group?
        user_is_member_of_group_that_created_ad = user in group_profile_of_group_that_purchased_ad.group_members.all() # Boolean: Is user member of this group?
        return user_created_ad or user_created_group_that_created_ad or user_is_member_of_group_that_created_ad # If any of the above three conditions is True, return True


class AdPurchaseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AdPurchase
    fields = AD_PURCHASE_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.user_that_purchased_ad = self.request.user
        # Make sure that if group is selected that user is part of that group:
        group = form.instance.group_that_purchased_ad
        if group is None:
            return super().form_valid(form)
        else: # Group is selected 
            group_profile = get_object_or_404(GroupProfile, group=group)
            if form.instance.user_that_purchased_ad == group_profile.group_creator or group_profile.group_members.filter(id=form.instance.user_that_purchased_ad.id).exists():
                return super().form_valid(form)
            else:
                return super().form_invalid(form)
        # Make sure that if a foreign key object is specified for
        # the ad type, then the appropriate item was created by
        # the user.


    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(AdPurchaseCreateView, self).get_context_data(**kwargs)
        header = "Purchase ad (to view plans, click <a href='/ads/offers/'><u>here</u></a>)"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class AdPurchaseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AdPurchase
    fields = AD_PURCHASE_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        user_created_ad_purchase = form.instance.user_that_purchased_ad == self.request.user # Boolean: Did user create the original AdPurchase object?
        group = form.instance.group_that_purchased_ad
        if user_created_ad_purchase and group is None:
            return super().form_valid(form)
        else: # Group is selected 
            group_profile = get_object_or_404(GroupProfile, group=group)
            if user_created_ad_purchase and (form.instance.user_that_purchased_ad == group_profile.group_creator or group_profile.group_members.filter(id=form.instance.user_that_purchased_ad.id).exists()):
                return super().form_valid(form)
            else:
                return super().form_invalid(form)

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(AdPurchaseUpdateView, self).get_context_data(**kwargs)
        header = "Update ad purchase"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class AdPurchaseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AdPurchase
    success_url = '/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(AdPurchaseDeleteView, self).get_context_data(**kwargs)
        item = get_object_or_404(AdPurchase, id=self.kwargs.get('pk'))
        title = f"Ad purchase: {item.title}"
        context.update({"type": "ad purchase", "title": title})
        return context

