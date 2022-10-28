import os
import stripe
import random

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from .models import Listing, Transaction
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import user_passes_test
from ecoles.models import Specialization, Course
from orgs.models import GroupProfile
from ecoles.datatools import generate_recommendations_from_queryset


def learning_carousel(request):
    return render(request, "market/LEARNING_CAROUSEL.html")

@login_required
def dashboard(request):
    return render(request, "market/dashboard/dashboard.html")

@login_required
def my_listings(request):
    listings = Listing.objects.filter(creator=request.user)
    context = {
        "items": listings
    }
    return render(request, "market/dashboard/user_listings.html", context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def transactions_admin(request):
    transactions = Transaction.objects.all()
    context = {
        "items": transactions
    }
    return render(request, "market/dashboard/transactions_admin.html", context)


class TransactionDetailView(UserPassesTestMixin, DetailView):
    model = Transaction

    def test_func(self):
        # transaction = get_object_or_404(Transaction, pk=kwargs['pk'])
        # if transaction.seller is request.user or transaction.purchaser is request.user:
        #     return True
        # return False
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        transaction = get_object_or_404(Transaction, pk=kwargs['pk'])
        context = {
            "transaction": transaction, 
            "user_is_seller": transaction.seller == request.user
        }
        if transaction.transaction_obj_type == 'listing':
            title = get_object_or_404(Listing, pk=transaction.transaction_obj_id)
            context.update({"title": title})
        return render(request, 'market/dashboard/transaction_detail.html', context)


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
            "num_results": num_results,
            "header": "All listings"
        })
        return context

    def get_queryset(self):
        return Listing.objects.all().exclude(visibility='Invisible').all().order_by('-title')


class ListingsByUserListView(UserPassesTestMixin, ListView):
    model = Listing
    template_name = 'market/listings.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(ListingsByUserListView, self).get_context_data(**kwargs)
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        results = Listing.objects.filter(creator=user_in_url).all()
        num_results = len(results)
        context.update({
            "num_results": num_results,
            "header": f"All listings by {user_in_url.username}"
        })
        return context

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return Listing.objects.filter(creator=user_in_url).all().exclude(visibility='Anonymous').all().exclude(visibility='Invisible').all().order_by('-title')


class ListingDetailView(UserPassesTestMixin, DetailView):
    model = Listing

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=kwargs['pk'])
        all_listings_from_this_creator = Listing.objects.filter(creator=listing.creator)

        recs = generate_recommendations_from_queryset(queryset=Listing.objects.all(), obj=listing)
        print(recs)

        context = {
            "item": listing, 
            "user_is_creator": listing.creator == request.user,
            "obj_type": "listing",
            "all_listings_from_this_creator": all_listings_from_this_creator,

            "recs": recs
        }

        return render(request, 'market/listing.html', context)


class ListingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Listing
    fields = ['title', 'description', 'price', 'date_due', 'visibility', 'listing_category', 'infinite_copies_available', 'quantity_available', 'listing_medium', 'group']
    template_name = 'market/dashboard/form_view.html' 

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # If user has chosen a group, make sure the user is a member of that group:
        group = form.instance.group
        if group is None:
            return super().form_valid(form)
        else: # Group is selected 
            group_profile = get_object_or_404(GroupProfile, group=group)
            if form.instance.creator == group_profile.group_creator or group_profile.group_members.filter(id=form.instance.creator.id).exists():
                return super().form_valid(form)
            else:
                return super().form_invalid(form)
        

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super(ListingCreateView, self).get_context_data(**kwargs)
        header = "Create listing"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    fields = ['title', 'description', 'price', 'date_due', 'visibility', 'listing_category', 'infinite_copies_available', 'quantity_available', 'listing_medium', 'group']
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # If user has chosen a group, make sure the user is a member of that group:
        group = form.instance.group
        if group is None:
            return super().form_valid(form)
        else: # Group is selected 
            group_profile = get_object_or_404(GroupProfile, group=group)
            if form.instance.creator == group_profile.group_creator or group_profile.group_members.filter(id=form.instance.creator.id).exists():
                return super().form_valid(form)
            else:
                return super().form_invalid(form)

    def test_func(self):
        return self.request.user == self.get_object().creator

    def get_context_data(self, **kwargs):
        context = super(ListingUpdateView, self).get_context_data(**kwargs)
        header = "Update Listing"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ListingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete Listing."""
    model = Listing
    success_url = '/market/listings/'
    context_object_name = 'item'
    template_name = 'market/confirm_delete.html'

    def test_func(self):
        return self.request.user == self.get_object().creator

    def get_context_data(self, **kwargs):
        context = super(ListingDeleteView, self).get_context_data(**kwargs)
        transaction = get_object_or_404(Listing, id=self.kwargs.get('pk'))
        title = f"Listing: {transaction.title}"
        context.update({"type": "listing", "title": title})
        return context


def purchase_logic(request, obj_type, item_id):
    item = None
    if obj_type == 'listing':
        item = Listing.objects.get(pk=item_id)
        item.purchasers.add(request.user)
    # If obj_type is course or specialization then also enroll
    elif obj_type == 'course':
        item = Course.objects.get(pk=item_id)
        # If obj_type is course then enroll in that course
        if not item.students.filter(id=request.user.id).exists():
            item.students.add(request.user)
        if not item.purchasers.filter(id=request.user.id).exists():
            item.purchasers.add(request.user)
    elif obj_type == 'specialization':
        item = Specialization.objects.get(pk=item_id)
        # If obj_type is specialization then 1) enroll in that specialization and 2) enroll in all courses within that specialization
        if not item.students.filter(id=request.user.id).exists():
            item.students.add(request.user)
        if not item.purchasers.filter(id=request.user.id).exists():
            item.purchasers.add(request.user)
        if isinstance(item, Specialization): # Affirm that obj is of type Specialization
            courses_within_specialization = Course.objects.filter(specialization=item) # Get all courses within specialization
            for course in courses_within_specialization: # For each of these courses within the specialization
                if not course.students.filter(id=request.user.id).exists(): # If user not already enrolled in that course
                    course.students.add(request.user) # Then add user as a student
    return item


def purchase_item_for_free(request, obj_type, pk):
    item = purchase_logic(request, obj_type, item_id=pk)
    if item is not None:
        print(item)
        # Generate Transaction record
        transaction_no = generate_transaction_id(10)
        transaction = Transaction.objects.create(transaction_obj_type=obj_type, transaction_obj_id=item.id, title=item.title, seller=item.creator, purchaser=request.user, transaction_id=transaction_no, value=item.price, description=f'Purchase of {obj_type}')
        transaction.save()         
        return render(request, 'payments/free_purchase_success.html', context={
            "obj_type": obj_type,
            "obj_id": pk
        }) 
    else:
        return redirect('payment_cancel')


#checkout call
def checkout(request, obj_type, pk):
    item = None
    if obj_type == 'listing':
        item = Listing.objects.get(pk=pk)
    elif obj_type == 'course':
        item = Course.objects.get(pk=pk)
    elif obj_type == 'specialization':
        item = Specialization.objects.get(pk=pk)
    if item is not None:
        context = {"item": item, "obj_type": obj_type}
        return render(request, "payments/checkout.html", context=context)
    return JsonResponse({"Error": "Item retrieval error."})

def checkout_session(request, obj_type, pk):
    stripe.api_key = os.environ.get('STRIPE_LIVE_KEY')
    item = None
    if obj_type == 'listing':
        item = Listing.objects.get(pk=pk)
    elif obj_type == 'course':
        item = Course.objects.get(pk=pk)
    elif obj_type == 'specialization':
        item = Specialization.objects.get(pk=pk)
    if item: # if item is not None
        print(obj_type * 100)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"{item.title} ({obj_type})",
                    },
                    'unit_amount': int(float(item.price * 100)),
                },
                'quantity': 1,
            }],
            mode='payment',
            #change domain name when you live it
            success_url=f'https://www.cadebruno.com/market/checkout/success/' + obj_type + "/" + str(pk) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=f'https://www.cadebruno.com/checkout/cancel/',

            client_reference_id=pk

        )
        return redirect(session.url, code=303)
    return JsonResponse({"Error": "Item retrieval error."})

#on stripe cancel payment
def payment_cancel(request):
    return render(request, "payments/cancel.html")

#generate transaction id
def generate_transaction_id(length):
    set_number = '12345678903773764673738299'
    import random
    gen_text = ''.join((random.choice(set_number)) for i in range(length))
    return gen_text

#stripe success payment
def payment_success(request, obj_type, pk):
    try:
        session = stripe.checkout.Session.retrieve(request.GET['session_id'])
        item_id = session.client_reference_id
        item = None
        if obj_type == 'listing':
            item = Listing.objects.get(pk=item_id)
        # If obj_type is course or specialization then also enroll
        elif obj_type == 'course':
            item = Course.objects.get(pk=item_id)
            # If obj_type is course then enroll in that course
            if not item.students.filter(id=request.user.id).exists():
                item.students.add(request.user)
            if not item.purchasers.filter(id=request.user.id).exists():
                item.purchasers.add(request.user)
        elif obj_type == 'specialization':
            item = Specialization.objects.get(pk=item_id)
            # If obj_type is specialization then 1) enroll in that specialization and 2) enroll in all courses within that specialization
            if not item.students.filter(id=request.user.id).exists():
                item.students.add(request.user)
            if not item.purchasers.filter(id=request.user.id).exists():
                item.purchasers.add(request.user)
            if isinstance(item, Specialization): # Affirm that obj is of type Specialization
                courses_within_specialization = Course.objects.filter(specialization=item) # Get all courses within specialization
                for course in courses_within_specialization: # For each of these courses within the specialization
                    if not course.students.filter(id=request.user.id).exists(): # If user not already enrolled in that course
                        course.students.add(request.user) # Then add user as a student


        if item is not None:
            # Generate Transaction record
            transaction_no = generate_transaction_id(10)
            Transaction.objects.create(transaction_obj_type=obj_type, transaction_obj_id=item.id, title=item.title, seller=item.creator, purchaser=request.user, transaction_id=transaction_no, value=item.price, description=f'Purchase of {obj_type}').save()
            # Render template
            return render(request, 'payments/success.html', context={
                "obj_type": obj_type
            }) 
        else:
            return render(request, 'payments/cancel.html')
    except:
        return render(request, 'payments/cancel.html')

#purchaser unverified payments
def my_payments(request):
    # transaction_verification_data=Transaction.objects.filter(purchaser=request.user,purchaser_verified=None)
    # return render(request,'payments/my_payments.html',{'transaction_verification_data':transaction_verification_data})
    return render(request,'payments/my_payments.html',{'items': Transaction.objects.filter(purchaser=request.user)})

def confirm_transaction(request, transaction_id):
    transaction_data=Transaction.objects.get(pk=transaction_id)
    transaction_data.purchaser_verified = True
    transaction_data.save()
    return redirect('my_payments')

def reject_transaction(request, transaction_id):
    transaction_data=Transaction.objects.get(pk=transaction_id)
    transaction_data.purchaser_verified = False
    transaction_data.save()
    return redirect('my_payments')


#fetch unverified payments for seller
