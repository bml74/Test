import os
import sys
import stripe
from decouple import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from users.models import Profile
from .models import Listing, Transaction, PaymentIntentTracker, SuggestedDelivery, Lottery, LotteryParticipant
from orgs.models import ListingForGroupMembers, RequestForPaymentToGroupMember
from ads.models import AdOffer, AdPurchase
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
    LISTING_FOR_GROUP_MEMBERS_FIELDS,
    TRANSACTION_DELIVERY_SUGGESTION_FIELDS
)
from config.abstract_settings import VARIABLES
from config.abstract_settings.template_names import (
    FORM_VIEW_TEMPLATE_NAME, 
    CONFIRM_DELETE_TEMPLATE_NAME
)
from config.utils import (
    formValid, 
    get_group_and_group_profile_from_group_id, 
    getGroupProfile, 
    is_ajax,
    runningDevServer,
    getDomain
)
from .utils import (
    get_group_and_group_profile_and_listing_from_listing_id,
    get_data_on_listing_for_group_members,
    create_payment_request_from_group_member,
    remove_payment_request_from_group_member,
    allowSaleBasedOnQuantity,
    handleQuantity,
    listing_category_options
)
from notifications.utils import sendEmail
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config.abstract_settings import VARIABLES


load_dotenv()


SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL_ADDRESS = os.getenv("SENDER_EMAIL_ADDRESS")


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
        if transaction.transaction_obj_type == VARIABLES.LISTING_OBJ_TYPE:
            title = get_object_or_404(Listing, pk=transaction.transaction_obj_id)
            context.update({"title": title})
        return render(request, 'market/dashboard/transaction_detail.html', context)


class TransactionDeliveryDetailView(UserPassesTestMixin, DetailView):
    model = Transaction

    def test_func(self):
        transaction = get_object_or_404(Transaction, pk=self.kwargs['transaction_pk'])
        if transaction.seller == self.request.user or transaction.purchaser == self.request.user:
            return True
        return False

    def get(self, request, *args, **kwargs):
        transaction = get_object_or_404(Transaction, pk=kwargs['transaction_pk'])
        if transaction.transaction_obj_type != VARIABLES.LISTING_OBJ_TYPE:
            return render(request, 'payments/transaction-no-delivery.html')
        else:
            listing = get_object_or_404(Listing, id=transaction.transaction_obj_id)
            if listing.listing_medium == "Digital File(s)" or listing.listing_medium == "Digital Service":
                return render(request, 'payments/transaction-no-delivery.html')        

        buyer_suggested_deliveries = SuggestedDelivery.objects.filter(transaction_id=transaction.id, created_by="Buyer").all()
        seller_suggested_deliveries = SuggestedDelivery.objects.filter(transaction_id=transaction.id, created_by="Seller").all()
        if transaction.delivery:
            accepted_delivery = transaction.delivery
        else: 
            accepted_delivery = None
        context = {
            "transaction": transaction, 
            "user_is_seller": transaction.seller == request.user,
            "buyer_suggested_deliveries": buyer_suggested_deliveries,
            "seller_suggested_deliveries": seller_suggested_deliveries,
            "header": f"Delivery for Transaction #{transaction.transaction_id}",
            "accepted_delivery": accepted_delivery
        }
        return render(request, 'payments/transaction-delivery.html', context)


class TransactionDeliveryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = SuggestedDelivery
    fields = TRANSACTION_DELIVERY_SUGGESTION_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME 

    def form_valid(self, form):
        transaction = get_object_or_404(Transaction, pk=self.kwargs['transaction_pk'])
        print(transaction)
        form.instance.transaction_id = self.kwargs['transaction_pk']
        print(form.instance.transaction_id)
        form.instance.seller = transaction.seller 
        print(form.instance.seller)
        form.instance.purchaser = transaction.purchaser
        print(form.instance.purchaser)
        if self.request.user == transaction.seller:
            form.instance.created_by = "Seller"
        else:
            form.instance.created_by = "Buyer"
        if self.request.user == transaction.seller or self.request.user == transaction.purchaser:
            return super().form_valid(form)
        return super().form_invalid(form)

    def test_func(self):
        transaction = get_object_or_404(Transaction, pk=self.kwargs['transaction_pk'])
        if transaction.seller == self.request.user or transaction.purchaser == self.request.user:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(TransactionDeliveryCreateView, self).get_context_data(**kwargs)
        transaction = get_object_or_404(Transaction, pk=self.kwargs['transaction_pk'])
        header = f"Add suggested delivery for Transaction #{transaction.transaction_id}"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


def set_delivery(request, transaction_pk, suggestion_pk):
    suggestion = get_object_or_404(SuggestedDelivery, id=suggestion_pk)
    suggestion.seller_verified = True
    suggestion.purchaser_verified = True
    suggestion.save()
    transaction = get_object_or_404(Transaction, id=transaction_pk)
    transaction.delivery = suggestion
    transaction.save()

    BASE_DOMAIN = getDomain()
    subject = "Delivery set"
    html_content = f"""
    <h3><strong>A delivery has been agreed upon for your transaction.</strong></h3>
    <h3><strong>Click <a href='{BASE_DOMAIN}/market/delivery/{transaction_pk}/'>here</a> to view details.</strong></h3>
    """
    sendEmail(subject=subject, html_content=html_content, to_emails=[transaction.seller.email, transaction.purchaser.email], from_email=SENDER_EMAIL_ADDRESS)

    return redirect('transaction-delivery', transaction_pk=transaction_pk)


def cancel_delivery(request, transaction_pk, suggestion_pk):
    suggestion = get_object_or_404(SuggestedDelivery, id=suggestion_pk)
    suggestion.seller_verified = False
    suggestion.purchaser_verified = False
    suggestion.save()
    transaction = get_object_or_404(Transaction, id=transaction_pk)
    transaction.delivery = None
    transaction.save()

    BASE_DOMAIN = getDomain()
    subject = "Delivery cancelled"
    html_content = f"""
    <h3><strong>The existing agreed-upon delivery has been cancelled.</strong></h3>
    <h3><strong>Click <a href='{BASE_DOMAIN}/market/delivery/{transaction_pk}/'>here</a> to view details and set up another delivery time and location.</strong></h3>
    """
    sendEmail(subject=subject, html_content=html_content, to_emails=[transaction.seller.email, transaction.purchaser.email], from_email=SENDER_EMAIL_ADDRESS)

    return redirect('transaction-delivery', transaction_pk=transaction_pk)


class ListingListView(UserPassesTestMixin, ListView):
    model = Listing
    template_name = 'market/listings.html'
    context_object_name = 'items'
    paginate_by = VARIABLES.PAGINATE_BY

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(ListingListView, self).get_context_data(**kwargs)
        results = (Listing.objects.filter(infinite_copies_available=True) | Listing.objects.filter(quantity_available__gt=0, infinite_copies_available=False)) & Listing.objects.filter(listing_type=VARIABLES.LOOKING_TO_SELL)
        num_results = len(results)
        
        """ BEGIN ADVERTISING LOGIC """
        ads_purchased_by_user = AdPurchase.objects.filter(user_that_purchased_ad=self.request.user).all()
        if len(ads_purchased_by_user) == 0:
            first_ads = second_ads = all_other_ads = None
        if len(ads_purchased_by_user) <= 3:
            first_ads = ads_purchased_by_user
            second_ads = None
            all_other_ads = None
        elif len(ads_purchased_by_user) > 3 and len(ads_purchased_by_user) <= 6:
            first_ads = ads_purchased_by_user[:3]
            second_ads = ads_purchased_by_user[3:6]
            all_other_ads = None
        else:
            first_ads = ads_purchased_by_user[:3]
            second_ads = ads_purchased_by_user[3:6]
            all_other_ads = ads_purchased_by_user[6:]
        for adPurchase in ads_purchased_by_user:
            adPurchase.impressions += 1
            if self.request.user not in adPurchase.unique_impressions.all():
                adPurchase.num_unique_impressions += 1
                adPurchase.unique_impressions.add(self.request.user)
            adPurchase.save()
        """ END ADVERTISING LOGIC """

        main_header = "For buyers"
        main_description = "Browse this page as a buyer and discover what other members of your community have that's available for sale."

        context.update({
            "listings_type": "offer-to-sell",
            "main_header": main_header,
            "main_description": main_description,
            "num_results": num_results,
            "header": "Users are looking to sell...",
            "user_has_stripe_account_id": get_object_or_404(Profile, user=self.request.user).stripe_account_id is not None,
            "first_ads": first_ads,
            "second_ads": second_ads,
            "all_other_ads": all_other_ads,
            "listing_category_options": listing_category_options
        })
        return context

    def get_queryset(self):
        results = (Listing.objects.filter(infinite_copies_available=True) | Listing.objects.filter(quantity_available__gt=0, infinite_copies_available=False)) & Listing.objects.filter(listing_type=VARIABLES.LOOKING_TO_SELL)
        return results.exclude(visibility='Invisible').all().order_by('-date_listed')


def request_or_offer(request):
    context = {
        "user_has_stripe_account_id": get_object_or_404(Profile, user=request.user).stripe_account_id is not None
    }
    return render(request, 'market/request_or_offer.html', context=context)


class ListingRequestsToBuyListView(UserPassesTestMixin, ListView):
    model = Listing
    template_name = 'market/listings.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(ListingRequestsToBuyListView, self).get_context_data(**kwargs)
        results = Listing.objects.filter(listing_type=VARIABLES.LOOKING_TO_BUY)
        num_results = len(results)
        main_header = "For sellers"
        main_description = "Browse this page as a seller and discover what other people in your community want. If they want something that you can provide, click 'Accept' to begin the transaction."
        context.update({
            "listings_type": "request-to-buy",
            "main_description": main_description,
            "main_header": main_header,
            "num_results": num_results,
            "header": "Users are looking to buy...",
            "user_has_stripe_account_id": get_object_or_404(Profile, user=self.request.user).stripe_account_id is not None
        })
        return context

    def get_queryset(self):
        results = Listing.objects.filter(listing_type=VARIABLES.LOOKING_TO_BUY)
        return results.exclude(visibility='Invisible').all().order_by('-date_listed')


def switch_listing(request, obj_type, pk):
    if obj_type == VARIABLES.LISTING_OBJ_TYPE:
        current_listing = Listing.objects.get(pk=pk)
        assert(current_listing.listing_type == VARIABLES.LOOKING_TO_BUY)
        new_listing = Listing(
            title=current_listing.title,
            image=current_listing.image,
            description=current_listing.description,
            price=current_listing.price,
            creator=request.user,
            group=current_listing.group if current_listing.group else None,
            visibility=current_listing.visibility,
            listing_type=VARIABLES.LOOKING_TO_SELL,
            listing_category=current_listing.listing_category,
            listing_medium=current_listing.listing_medium,
            infinite_copies_available=current_listing.infinite_copies_available,
            quantity_available=current_listing.quantity_available,
            quantity_sold=current_listing.quantity_sold
        )
        new_listing.save()
        # Send e-mail to creator of Bid listing
        try:
            BASE_DOMAIN = getDomain()

            # EMAIL TO NEW CREATOR
            subject = f"Listing created"
            html_content = f"""
            Your listing has been created. You can view this new listing <a href="{BASE_DOMAIN}/market/listing/{new_listing.id}/">here</a>.{current_listing.creator.email} has been emailed to inform them of this update.  
            """
            message = Mail(from_email="bml74@georgetown.edu", to_emails=request.user.email, subject=subject, html_content=html_content)
            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            response1 = sg.send(message)
            print(response1)

            # EMAIL TO REQUESTER
            subject = f"Request accepted"
            html_content = f"""
            {current_listing.creator.username} has accepted your request to buy '{current_listing.title}'. You can view this new listing <a href="{BASE_DOMAIN}/market/listing/{new_listing.id}/">here</a>.  
            """
            message = Mail(from_email="bml74@georgetown.edu", to_emails=request.user.email, subject=subject, html_content=html_content)
            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            response2 = sg.send(message)
        except Exception as e:
            print(e)
        return redirect('listing', pk=new_listing.id) # Return redirect to new listing
    return redirect('listing', pk=pk) # Return redirect to original listing


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
        return Listing.objects.filter(creator=user_in_url).all().exclude(visibility='Anonymous').all().exclude(visibility='Invisible').all().order_by('-date_listed')


class ListingDetailView(UserPassesTestMixin, DetailView):
    model = Listing

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        listing = get_object_or_404(Listing, pk=kwargs['pk'])
        all_listings_from_this_creator = Listing.objects.filter(creator=listing.creator)

        # recs = generate_recommendations_from_queryset(queryset=Listing.objects.all(), obj=listing)
        # print(recs)

        from users.views import getOverallRating
        overall_rating = getOverallRating(user_being_rated=listing.creator)

        context = {
            "item": listing, 
            "user_is_creator": listing.creator == request.user,
            "obj_type": "listing",
            "all_listings_from_this_creator": all_listings_from_this_creator,

            # "recs": recs,

            "overall_rating": overall_rating
        }

        return render(request, 'market/listing.html', context)


class ListingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Listing
    fields = LISTING_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME 

    def form_valid(self, form): 
        form.instance.creator = self.request.user
        listings_type = self.kwargs.get('listings_type')
        if listings_type == "offer-to-sell":
            form.instance.listing_type = VARIABLES.LOOKING_TO_SELL
        else: # "request-to-buy"
            form.instance.listing_type = VARIABLES.LOOKING_TO_BUY
        # If user has chosen a group, make sure the user is a member of that group:
        return super().form_valid(form) if formValid(user=form.instance.creator, group=form.instance.group) else super().form_invalid(form)

    def test_func(self):
        return self.request.user.is_authenticated and get_object_or_404(Profile, user=self.request.user).stripe_account_id is not None

    def get_context_data(self, **kwargs):
        context = super(ListingCreateView, self).get_context_data(**kwargs)
        listings_type = self.kwargs.get('listings_type')
        if listings_type == "offer-to-sell":
            header = "Post something that you want to sell"
        else: # "request-to-buy"
            header = "Post something that you want to buy"
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
    if obj_type == VARIABLES.LISTING_OBJ_TYPE:
        item = Listing.objects.get(pk=item_id)
        item.purchasers.add(request.user)
    elif obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:
        item = ListingForGroupMembers.objects.get(pk=item_id)
        item.members_who_have_paid.add(request.user)
    # If obj_type is course or specialization then also enroll
    elif obj_type == VARIABLES.COURSE_OBJ_TYPE:
        item = Course.objects.get(pk=item_id)
        # If obj_type is course then enroll in that course
        if not item.students.filter(id=request.user.id).exists():
            item.students.add(request.user)
        if not item.purchasers.filter(id=request.user.id).exists():
            item.purchasers.add(request.user)
    elif obj_type == VARIABLES.SPECIALIZATION_OBJ_TYPE:
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


def checkout(request, obj_type, pk):
    item = None
    if runningDevServer():
        stripe.api_key = config('STRIPE_TEST_KEY') 
        publishable_key = config('STRIPE_PUBLISHABLE_TEST_KEY') 
        BASE_DOMAIN = VARIABLES.LOCAL_DOMAIN
    else:
        stripe.api_key = config('STRIPE_LIVE_KEY')
        publishable_key = config('STRIPE_PUBLISHABLE_LIVE_KEY') 
        BASE_DOMAIN = VARIABLES.HOSTED_DOMAIN
    payment_intent_id = None
    payment_intent_client_secret = None
    if obj_type == VARIABLES.LISTING_OBJ_TYPE or obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:
        if obj_type == VARIABLES.LISTING_OBJ_TYPE:
            item = Listing.objects.get(pk=pk)
            creator_user_profile = Profile.objects.get(user_id=item.creator.id) 
        elif obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:
            item = ListingForGroupMembers.objects.get(pk=pk)
            group = item.group
            group_profile = getGroupProfile(group=group)
            creator_user_profile = Profile.objects.get(user_id=group_profile.group_creator.id) 

        if creator_user_profile.stripe_account_id and len(creator_user_profile.stripe_account_id) > 1:
            stripe_account_id = creator_user_profile.stripe_account_id

            commission_fee = VARIABLES.COMMISSION_FEE # commission fee
            price_rounded = round(item.price, 2)
            total_payment_amount = int(price_rounded * 100)
            payout_amount = int(total_payment_amount - (total_payment_amount * commission_fee))

            market_paymentintent = None
            try:
                market_paymentintent = PaymentIntentTracker.objects.get(
                    user_id=request.user.id, 
                    listing_id=item.id,
                    stripe_account_id=stripe_account_id
                )
            except PaymentIntentTracker.DoesNotExist:
                market_paymentintent = None

            print('market_paymentintent', market_paymentintent)

            if(market_paymentintent is not None):
                # Reuse existing payment intent id
                payment_intent_id = market_paymentintent.stripe_payment_intent_id
                # Update payment intent in case of any listing price changes
                stripe.PaymentIntent.modify( 
                    payment_intent_id,
                    amount=total_payment_amount,
                    currency='usd',
                    payment_method_types=VARIABLES.STRIPE_PAYMENT_METHOD_TYPES,
                    transfer_data={
                        'amount': payout_amount
                    }
                ) 
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                payment_intent_client_secret = payment_intent.client_secret
            else:
                payment_intent = stripe.PaymentIntent.create(
                    amount=total_payment_amount,
                    currency='usd',
                    payment_method_types=VARIABLES.STRIPE_PAYMENT_METHOD_TYPES,
                    transfer_data={
                        'amount': payout_amount,
                        'destination': stripe_account_id
                    }
                )
                payment_intent_id = payment_intent.id
                payment_intent_client_secret = payment_intent.client_secret
                PaymentIntentTracker(
                    stripe_payment_intent_id = payment_intent_id,
                    stripe_account_id = stripe_account_id,
                    listing_id=item.id,
                    user_id=request.user.id
                ).save()
    elif obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:
        item = ListingForGroupMembers.objects.get(pk=pk)
    elif obj_type == VARIABLES.COURSE_OBJ_TYPE:
        item = Course.objects.get(pk=pk)
    elif obj_type == VARIABLES.SPECIALIZATION_OBJ_TYPE:
        item = Specialization.objects.get(pk=pk)
    elif obj_type == VARIABLES.AD_OFFER_OBJ_TYPE:
        item = AdOffer.objects.get(pk=pk)
    if item is not None:
        context = {
            "item": item, 
            "obj_type": obj_type, 
            "payment_intent_id": payment_intent_id,
            "payment_intent_client_secret": payment_intent_client_secret,
            "publishable_key": publishable_key,
            "BASE_DOMAIN": BASE_DOMAIN
        }
        return render(request, "payments/checkout.html", context=context)
    return JsonResponse({"Error": "Item retrieval error."})


def checkout_session(request, obj_type, pk):

    if runningDevServer():
        BASE_DOMAIN = VARIABLES.LOCAL_DOMAIN
        stripe.api_key = config('STRIPE_TEST_KEY') 
    else:
        BASE_DOMAIN = VARIABLES.HOSTED_DOMAIN
        stripe.api_key = config('STRIPE_LIVE_KEY')

    item = None
    if obj_type == VARIABLES.LISTING_OBJ_TYPE:
        item = Listing.objects.get(pk=pk)
    elif obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:
        item = ListingForGroupMembers.objects.get(pk=pk)
    elif obj_type == VARIABLES.COURSE_OBJ_TYPE:
        item = Course.objects.get(pk=pk)
    elif obj_type == VARIABLES.SPECIALIZATION_OBJ_TYPE:
        item = Specialization.objects.get(pk=pk)
    elif obj_type == VARIABLES.AD_OFFER_OBJ_TYPE:
        item = AdOffer.objects.get(pk=pk)
    if item: # if item is not None

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


def payment_cancel(request):
    return render(request, "payments/cancel.html")


def generate_transaction_id(length):
    set_number = '12345678903773764673738299'
    import random
    gen_text = ''.join((random.choice(set_number)) for i in range(length))
    return gen_text


def payment_success(request, obj_type, pk):
    if obj_type == VARIABLES.LISTING_OBJ_TYPE:
        item = purchase_logic(request, obj_type, item_id=pk)
    elif obj_type == VARIABLES.AD_OFFER_OBJ_TYPE:
        item = AdOffer.objects.get(pk=pk)
    try:

        if runningDevServer():
            stripe.api_key = config('STRIPE_TEST_KEY') 
        else:
            stripe.api_key = config('STRIPE_LIVE_KEY')

        item_id = None
        stripe_payment_intent_details = None

        is_custom_checkout = False
        try:
            is_custom_checkout = request.GET['custom_checkout'] and request.GET['custom_checkout'] == 'true'
        except:
            is_custom_checkout = False

        if is_custom_checkout == True:
            item_id = request.GET['session_id']
            stripe_payment_intent_details = stripe.PaymentIntent.retrieve(request.GET['session_id'])
            try:
                # Delete payment method id from records after successful payment. Payment Intent ID cannot be reused once a payment goes through.
                PaymentIntentTracker.objects.filter(stripe_payment_intent_id=request.GET['session_id']).delete()
            except:
                print('Error deleting payment intent from records')
        else:
            session = stripe.checkout.Session.retrieve(request.GET['session_id'])
            item_id = session.client_reference_id

        item = None
        if obj_type == VARIABLES.LISTING_OBJ_TYPE:
            item = Listing.objects.get(pk=pk)
            if not allowSaleBasedOnQuantity(item):
                return JsonResponse({"Error": "There are not enough of these items available."})
            else: 
                handleQuantity(item)
        elif obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:
            item = ListingForGroupMembers.objects.get(pk=pk)
            # If there are existing requests, delete.
            if RequestForPaymentToGroupMember.objects.filter(user_receiving_request=request.user, listing_for_group_members=item).exists():
                for req in RequestForPaymentToGroupMember.objects.filter(user_receiving_request=request.user, listing_for_group_members=item).all():
                    req.delete()
            item.members_who_have_paid.add(request.user)
        # If obj_type is course or specialization then also enroll
        elif obj_type == VARIABLES.COURSE_OBJ_TYPE:
            item = Course.objects.get(pk=pk)
            # If obj_type is course then enroll in that course
            if not item.students.filter(id=request.user.id).exists():
                item.students.add(request.user)
            if not item.purchasers.filter(id=request.user.id).exists():
                item.purchasers.add(request.user)
        elif obj_type == VARIABLES.SPECIALIZATION_OBJ_TYPE:
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
        elif obj_type == VARIABLES.AD_OFFER_OBJ_TYPE:
            item = AdOffer.objects.get(pk=pk)
            ad_purchase = AdPurchase(
                user_that_purchased_ad=request.user,
                offer=item
            )
            ad_purchase.save()
        if item is not None:
            transaction_no = generate_transaction_id(10) # Generate Transaction record
            t = Transaction(
                transaction_obj_type=obj_type, 
                transaction_obj_id=item.pk, 
                title=item.title, 
                purchaser=request.user, 
                transaction_id=transaction_no, 
                value=float(item.price), 
                description=f'Purchase of {obj_type}'
            )
            try:
                if item.creator:
                    t.seller = item.creator
            except:
                pass

            t.save()

            if obj_type == VARIABLES.LISTING_OBJ_TYPE:
                BASE_DOMAIN = getDomain()
                # FOR SELLER:
                subject = "Sale successful"
                html_content = f"""
                <h3><strong>The user "{t.purchaser}" has bought "{item.title}" from you for ${t.value}.</strong></h3>
                <h3><strong>Click <a href='{BASE_DOMAIN}/market/delivery/{t.id}/'>here</a> to set a delivery.</strong></h3>
                <h3><strong>Click <a href='{BASE_DOMAIN}/market/transactions/{t.id}/'>here</a> to view transaction details.</strong></h3>
                <h3><strong>Click <a href='{BASE_DOMAIN}/market/my_sales/'>here</a> to view all your sales.</strong></h3>
                """
                sendEmail(subject=subject, html_content=html_content, to_emails=t.seller.email, from_email=SENDER_EMAIL_ADDRESS)
                # FOR BUYER:
                subject = "Purchase successful"
                html_content = f"""
                <h3><strong>Your purchase of {item.title} was successful!.</strong></h3>
                <h3><strong>Click <a href='{BASE_DOMAIN}/market/delivery/{t.id}/'>here</a> to set a delivery.</strong></h3>
                <h3><strong>Click <a href='{BASE_DOMAIN}/market/transactions/{t.id}/'>here</a> to view transaction details.</strong></h3>
                <h3><strong>Click <a href='{BASE_DOMAIN}/market/my_purchases/'>here</a> to view all your purchases.</strong></h3>
                """
                sendEmail(subject=subject, html_content=html_content, to_emails=t.purchaser.email, from_email=SENDER_EMAIL_ADDRESS)


            
            return render(request, 'payments/success.html', context={
                "obj_type":  obj_type,
                "session_id": item_id,
                "custom_checkout": is_custom_checkout
            }) 
        else:
            return render(request, 'payments/cancel.html')
    except Exception as e:
        return render(request, 'payments/cancel.html')


def my_payments(request):
    # transaction_verification_data=Transaction.objects.filter(purchaser=request.user,purchaser_verified=None)
    # return render(request,'payments/my_payments.html',{'transaction_verification_data':transaction_verification_data})
    items = list(set(list(Transaction.objects.filter(purchaser=request.user)) + list(Transaction.objects.filter(seller=request.user)))).reverse()
    return render(request,'payments/my_payments.html',{'items': items})


def my_purchases(request):
    # transaction_verification_data=Transaction.objects.filter(purchaser=request.user,purchaser_verified=None)
    # return render(request,'payments/my_payments.html',{'transaction_verification_data':transaction_verification_data})
    items = list(Transaction.objects.filter(purchaser=request.user).order_by('-inserted_on'))
    return render(request,'payments/my_purchases_sales.html',{"items": items, "header": "My purchases"})


def my_sales(request):
    items = list(Transaction.objects.filter(seller=request.user).order_by('-inserted_on'))
    return render(request,'payments/my_purchases_sales.html',{"items": items, "header": "My sales"})


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

        list_of_members_attending = list(listing_for_group_members.members_attending_event.all())

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
            "user_is_attending_event": "true" if request.user in listing_for_group_members.members_attending_event.all() else "false",
            "list_of_members_attending": list_of_members_attending
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
    listing_for_group_members = get_object_or_404(ListingForGroupMembers, id=listing_for_group_members_id)
    try:
        BASE_DOMAIN = getDomain()
        subject = f"Payment request"
        html_content = f"""
        <h3><strong>{group.name} has requested a payment from you for {listing_for_group_members.title}.</strong></h3>
        <h3><strong>Click <a href='{BASE_DOMAIN}/market/checkout/listing_for_group_members/{listing_for_group_members_id}/'>here</a> to pay.</strong></h3>
        <h3><strong>Click <a href='{BASE_DOMAIN}/market/my/payment_requests/'>here</a> to view all payments requested from you.</strong></h3>
        """
        message = Mail(from_email="bml74@georgetown.edu", to_emails=user_receiving_request.email, subject=subject, html_content=html_content)
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
    except Exception as e:
        print(e)
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
    context_object_name = "payment_requests"

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(RequestForPaymentToGroupMemberListView, self).get_context_data(**kwargs)
        context.update({
            "obj_type": "listing_for_group_members"
        })

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
        return self.request.user.is_authenticated and get_object_or_404(Profile, user=self.request.user).stripe_account_id is not None

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


class LotteryDetailView(UserPassesTestMixin, DetailView):
    model = Lottery

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        lottery = get_object_or_404(Lottery, pk=kwargs['pk'])

        winner = None
        num_entries_for_user = pct_chance = num_entries = 0
        if not lottery.winner:
            num = lottery.select_lucky_number()
            if num and LotteryParticipant.objects.filter(fk_lottery=lottery).exists():
                participants = LotteryParticipant.objects.filter(fk_lottery=lottery)
                if participants:
                    winning_entry = participants[num]
                    winner = lottery.winner = winning_entry.lottery_participant
                    lottery.save()
                    if winner:
                        try:
                            BASE_DOMAIN = getDomain()
                            subject = f"Congratulations!"
                            html_content = f"""
                            Congratulations, {winner}! You have won the lottery and will receive your prize {lottery.prize} shortly.
                            """
                            message = Mail(from_email="bml74@georgetown.edu", to_emails=winner.email, subject=subject, html_content=html_content)
                            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
                            response = sg.send(message)
                            print(response.status_code)
                            print(response.body)
                            print(response.headers)
                        except Exception as e:
                            print(e)
            participants = LotteryParticipant.objects.filter(fk_lottery=lottery)
            num_entries = len(participants)
            num_entries_for_user = len(LotteryParticipant.objects.filter(fk_lottery=lottery, lottery_participant=request.user))
            try:
                pct_chance = (num_entries_for_user / num_entries) * 100
            except ZeroDivisionError:
                pct_chance = 0
        
        context = {
            "lottery": lottery,
            "user_profile": get_object_or_404(Profile, user=request.user),
            "winner": winner,
            "num_entries_for_user": num_entries_for_user, 
            "num_entries": num_entries,
            "pct_chance": pct_chance
        }

        return render(request, 'market/lottery.html', context)


def add_lottery_participant(request, lottery_pk):
    profile = get_object_or_404(Profile, user=request.user)
    lottery = get_object_or_404(Lottery, id=lottery_pk)
    if not lottery.winner:
        REQUIRED_CREDITS_TO_ENTER = VARIABLES.NUM_CREDITS_TO_ENTER_LOTTERY
        if profile.credits >= REQUIRED_CREDITS_TO_ENTER:
            if not LotteryParticipant.objects.filter(lottery_participant=request.user, fk_lottery=lottery).exists():
                print(len(LotteryParticipant.objects.filter(lottery_participant=request.user, fk_lottery=lottery)))
                print(LotteryParticipant.objects.filter(lottery_participant=request.user, fk_lottery=lottery))
                lottery.num_unique_users += REQUIRED_CREDITS_TO_ENTER
                lottery.save()
            new_entry = LotteryParticipant(lottery_participant=request.user, fk_lottery=lottery)
            new_entry.save()
            profile.credits -= REQUIRED_CREDITS_TO_ENTER
            profile.save()
            messages.success(request, f'You have been entered in the lottery!')
    return redirect('lottery', pk=lottery.id)


class LotteryListView(UserPassesTestMixin, ListView):
    model = Lottery
    template_name = 'market/lotteries.html'
    context_object_name = 'items'
    paginate_by = VARIABLES.PAGINATE_BY

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(LotteryListView, self).get_context_data(**kwargs)
        context.update({
            
        })
        return context

    def get_queryset(self):
        results = Lottery.objects.all()
        return results.order_by('-date_created')


def redirect_from_ad_to_listing(request, pk):
    adPurchase = get_object_or_404(AdPurchase, id=pk)
    adPurchase.clicks += 1
    return redirect('listing', pk=adPurchase.listing_to_be_advertised.id)