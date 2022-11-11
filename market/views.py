import os, sys
import stripe
from decouple import config
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from .models import Listing, Transaction
from orgs.models import ListingForGroupMembers, RequestForPaymentToGroupMember
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from ecoles.models import Specialization, Course
from ecoles.datatools import generate_recommendations_from_queryset
from config.abstract_settings.model_fields import (
    LISTING_FIELDS,
    LISTING_FOR_GROUP_MEMBERS_FIELDS
)
from config.abstract_settings.template_names import (
    FORM_VIEW_TEMPLATE_NAME, 
    CONFIRM_DELETE_TEMPLATE_NAME
)
from config.utils import formValid, get_group_and_group_profile_from_group_id, getGroupProfile, is_ajax
from .utils import (
    get_group_and_group_profile_and_listing_from_listing_id,
    get_data_on_listing_for_group_members,
    create_payment_request_from_group_member,
    remove_payment_request_from_group_member
)


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
    fields = LISTING_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME 

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # If user has chosen a group, make sure the user is a member of that group:
        return super().form_valid(form) if formValid(user=form.instance.creator, group=form.instance.group) else super().form_invalid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(ListingCreateView, self).get_context_data(**kwargs)
        header = "Create listing"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ListingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Listing
    fields = LISTING_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # If user has chosen a group, make sure the user is a member of that group:
        return super().form_valid(form) if formValid(user=form.instance.creator, group=form.instance.group) else super().form_invalid(form)

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
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

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
    elif obj_type == 'listing_for_group_members':
        item = ListingForGroupMembers.objects.get(pk=item_id)
        item.members_who_have_paid.add(request.user)
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
    elif obj_type == 'listing_for_group_members':
        item = ListingForGroupMembers.objects.get(pk=pk)
    elif obj_type == 'course':
        item = Course.objects.get(pk=pk)
    elif obj_type == 'specialization':
        item = Specialization.objects.get(pk=pk)
    if item is not None:
        try:
            # If user created item, then don't let them view checkout page and purchase.
            if item.creator == request.user:
                return JsonResponse({"Error": "The creator of this item cannot purchase the same item."})
        except:
            pass
        context = {"item": item, "obj_type": obj_type}
        return render(request, "payments/checkout.html", context=context)
    return JsonResponse({"Error": "Item retrieval error."})


def checkout_session(request, obj_type, pk):

    RUNNING_DEVSERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')

    if RUNNING_DEVSERVER:
        BASE_DOMAIN = 'http://127.0.0.1:8000' 
        stripe.api_key = config('STRIPE_TEST_KEY') 
    else:
        BASE_DOMAIN = 'https://www.cadebruno.com'
        stripe.api_key = config('STRIPE_LIVE_KEY')

    item = None
    if obj_type == 'listing':
        item = Listing.objects.get(pk=pk)
    elif obj_type == 'listing_for_group_members':
        item = ListingForGroupMembers.objects.get(pk=pk)
        print(item)
        print("from checkout_session function")
    elif obj_type == 'course':
        item = Course.objects.get(pk=pk)
    elif obj_type == 'specialization':
        item = Specialization.objects.get(pk=pk)
    if item: # if item is not None
        if obj_type in ['listing', 'course', 'specialization']:
            if item.creator == request.user:
                return JsonResponse({"Error": "The creator of this item cannot purchase the same item."})
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"{item.title} ({' '.join(obj_type.split('_'))})",
                    },
                    'unit_amount': int(float(item.price * 100)),
                },
                'quantity': 1,
            }],
            mode='payment',
            #change domain name when you live it
            success_url=f'{BASE_DOMAIN}/market/success/checkout/' + obj_type + "/" + str(pk) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=f'{BASE_DOMAIN}/market/cancel/checkout/',

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
            item = Listing.objects.get(pk=pk)
        elif obj_type == 'listing_for_group_members':
            item = ListingForGroupMembers.objects.get(pk=pk)
            # If there are existing requests, delete.
            if RequestForPaymentToGroupMember.objects.filter(user_receiving_request=request.user, listing_for_group_members=item).exists():
                for req in RequestForPaymentToGroupMember.objects.filter(user_receiving_request=request.user, listing_for_group_members=item).all():
                    req.delete()
            item.members_who_have_paid.add(request.user)
        # If obj_type is course or specialization then also enroll
        elif obj_type == 'course':
            item = Course.objects.get(pk=pk)
            # If obj_type is course then enroll in that course
            if not item.students.filter(id=request.user.id).exists():
                item.students.add(request.user)
            if not item.purchasers.filter(id=request.user.id).exists():
                item.purchasers.add(request.user)
        elif obj_type == 'specialization':
            item = Specialization.objects.get(pk=pk)
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

            print(item)
            print(type(item))
            print("from payment success function")
            print(obj_type)
            print(item.id)
            print(item.title)
            print(item.price)

            t = Transaction(
                transaction_obj_type=obj_type, 
                transaction_obj_id=item.pk, 
                title=item.title, 
                purchaser=request.user, 
                transaction_id=transaction_no, 
                value=float(item.price), 
                description=f'Purchase of obj_type'
            )
            try:
                if item.creator:
                    t.seller = item.creator
            except:
                pass

            t.save()
            # Render template
            print(t)
            return render(request, 'payments/success.html', context={
                "obj_type":  obj_type
            }) 
        else:
            return render(request, 'payments/cancel.html')
    except:
        return render(request, 'payments/cancel.html')


#purchaser unverified payments
def my_payments(request):
    # transaction_verification_data=Transaction.objects.filter(purchaser=request.user,purchaser_verified=None)
    # return render(request,'payments/my_payments.html',{'transaction_verification_data':transaction_verification_data})
    items = set(list(Transaction.objects.filter(purchaser=request.user)) + list(Transaction.objects.filter(seller=request.user)))
    return render(request,'payments/my_payments.html',{'items': items})


def my_sales(request):
    items = list(Transaction.objects.filter(seller=request.user))
    return render(request,'payments/my_sales.html',{'items': items})


def confirm_transaction(request, transaction_id):
    transaction_data=Transaction.objects.get(pk=transaction_id)
    if request.user == transaction_data.purchaser:
        transaction_data.purchaser_verified = True
    else:
        transaction_data.seller_verified = True
    transaction_data.save()
    return redirect('my_payments')


def reject_transaction(request, transaction_id):
    transaction_data=Transaction.objects.get(pk=transaction_id)
    if request.user == transaction_data.purchaser:
        transaction_data.purchaser_verified = False
    else:
        transaction_data.seller_verified = False
    transaction_data.save()
    return redirect('my_payments')


"""
Tutoring:
- User signs up with georgetown.edu address
- Specifies they want to be a tutor
- Sends transcript
- We check that they completed the classes necessary
- If yes then we allow them to be a tutor
"""


class ListingForGroupMembersDetailView(UserPassesTestMixin, DetailView):
    model = ListingForGroupMembers

    def test_func(self):
        (group, group_profile, listing_for_group_members) = get_group_and_group_profile_and_listing_from_listing_id(ListingForGroupMembers_obj_id=int(self.kwargs['pk']))
        return self.request.user.is_authenticated and self.request.user in group_profile.group_members.all()

    def get(self, request, *args, **kwargs):
        (group, group_profile, listing_for_group_members, list_of_members_who_have_paid, list_of_members_who_have_not_paid) = get_data_on_listing_for_group_members(ListingForGroupMembers_obj_id=int(kwargs['pk']))

        user_is_creator_of_group = self.request.user == group_profile.group_creator

        existing_requests_for_this_listing = list(
            RequestForPaymentToGroupMember.objects.filter(listing_for_group_members=listing_for_group_members).all()
        )
        users_who_have_received_payment_request = [req.user_receiving_request for req in existing_requests_for_this_listing]

        context = {
            "item": listing_for_group_members,
            "obj_type": "listing_for_group_members",
            "group": group,
            "group_profile": group_profile,
            "user_is_creator_of_group": user_is_creator_of_group,
            "members": group_profile.group_members.all(),
            "list_of_members_who_have_paid": list_of_members_who_have_paid,
            "list_of_members_who_have_not_paid": list_of_members_who_have_not_paid,
            "users_who_have_received_payment_request": users_who_have_received_payment_request,
            "user_is_attending_event": "true" if request.user in listing_for_group_members.members_attending_event.all() else "false"
        }

        if is_ajax(request):
            user_is_attending_event = request.GET.get('user_is_attending_event')
            print(".")
            print(user_is_attending_event)
            username_of_attending_event = request.GET.get('username_of_attending_event')
            print(username_of_attending_event)
            user = get_object_or_404(User, username=username_of_attending_event)
            print(".")
            listing_for_group_members_id = request.GET.get('listing_for_group_members_id')
            listing_for_group_members = get_object_or_404(ListingForGroupMembers, id=listing_for_group_members_id)
            if user_is_attending_event == "true":
                listing_for_group_members.members_attending_event.add(request.user)
                context.update({"user_is_attending_event": "true"})
                return JsonResponse({"user_is_attending_event": "true"})
            else:
                listing_for_group_members.members_attending_event.remove(request.user)
                context.update({"user_is_attending_event": "false"})
                return JsonResponse({"user_is_attending_event": "false"})

        return render(request, 'market/listing_for_group_members.html', context)


def request_payment(request, group_id, user_id, listing_for_group_members_id):
    (group, group_profile) = get_group_and_group_profile_from_group_id(
        group_id=group_id
    )
    user_sending_request = group_profile.group_creator
    user_receiving_request = get_object_or_404(User, id=user_id)
    create_payment_request_from_group_member(
        user_sending_request=user_sending_request,
        user_receiving_request=user_receiving_request,
        ListingForGroupMembers_obj_id=listing_for_group_members_id
    ) # Function returns a Bool.
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def reject_payment_request(request, group_id, user_id, listing_for_group_members_id):
    (group, group_profile) = get_group_and_group_profile_from_group_id(
        group_id=group_id
    )
    user_sending_request = group_profile.group_creator
    user_receiving_request = get_object_or_404(User, id=user_id)
    remove_payment_request_from_group_member(
        user_sending_request=user_sending_request,
        user_receiving_request=user_receiving_request,
        ListingForGroupMembers_obj_id=listing_for_group_members_id
    ) # Function returns a Bool.
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


class RequestForPaymentToGroupMemberListView(UserPassesTestMixin, ListView):
    model = RequestForPaymentToGroupMember
    template_name = 'market/payment_requests.html'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(RequestForPaymentToGroupMemberListView, self).get_context_data(**kwargs)
        context.update({
            "obj_type": "listing_for_group_members"
        })

        RUNNING_DEVSERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')

        if RUNNING_DEVSERVER:
            print('PMT_TEST_KEY') 
        else:
            print('PMT_LIVE_KEY')

        return context

    def get_queryset(self):
        reqs = RequestForPaymentToGroupMember.objects.filter(user_receiving_request=self.request.user).all()
        return reqs


class ListingForGroupMembersCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = ListingForGroupMembers
    fields = LISTING_FOR_GROUP_MEMBERS_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME 

    def form_valid(self, form):
        form.instance.group = get_object_or_404(Group, id=self.kwargs.get('group_id'))
        group = form.instance.group
        group_profile = getGroupProfile(group=group)
        user = self.request.user
        if user == group_profile.group_creator:
            return super().form_valid(form) 
        super().form_invalid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(ListingForGroupMembersCreateView, self).get_context_data(**kwargs)
        header = "Create listing for group members"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ListingForGroupMembersUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ListingForGroupMembers
    fields = LISTING_FOR_GROUP_MEMBERS_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.group = get_object_or_404(Group, id=self.kwargs.get('group_id'))
        group = form.instance.group
        group_profile = getGroupProfile(group=group)
        user = self.request.user
        if user == group_profile.group_creator:
            return super().form_valid(form) 
        super().form_invalid(form)

    def test_func(self):
        return self.request.user == self.get_object().creator

    def get_context_data(self, **kwargs):
        context = super(ListingForGroupMembersUpdateView, self).get_context_data(**kwargs)
        header = "Create listing for group members"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class ListingForGroupMembersDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ListingForGroupMembers
    success_url = '/market/listings/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        return self.request.user == self.get_object().group.group_creator

    def get_context_data(self, **kwargs):
        context = super(ListingForGroupMembersDeleteView, self).get_context_data(**kwargs)
        item = get_object_or_404(ListingForGroupMembers, id=self.kwargs.get('pk'))
        title = f"Listing for group members: {item.title}"
        context.update({"type": "listing_for_group_members", "title": title})
        return context




