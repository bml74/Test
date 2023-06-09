import os
import sys
import stripe
from decouple import config
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User, Group
from users.models import Profile, Notification
from .models import Listing, Transaction, PaymentIntentTracker, SuggestedDelivery, Lottery, LotteryParticipant, RequestForDigitalTicket, TicketFile
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
    TRANSACTION_DELIVERY_SUGGESTION_FIELDS,
    TICKET_FILE_FIELDS
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
    getDomain,
    create_notification
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
        listing = get_object_or_404(Listing, id=transaction.transaction_obj_id)
        clothing = True if listing.listing_category in VARIABLES.CLOTHING_OPTIONS else False
        context = {
            "transaction": transaction, 
            "user_is_seller": transaction.seller == request.user,
            "clothing": clothing
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
        form.instance.transaction_id = self.kwargs['transaction_pk']
        form.instance.seller = transaction.seller 
        form.instance.purchaser = transaction.purchaser
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
    

class SizeSelectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Transaction
    fields = ['size']
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        transaction = get_object_or_404(Transaction, id=self.kwargs.get('pk'))
        if self.request.user == transaction.purchaser:
            if transaction.transaction_obj_type == "listing":
                listing = get_object_or_404(Listing, id=transaction.transaction_obj_id)
                if listing.listing_category in VARIABLES.CLOTHING_OPTIONS:
                    return True
        return False

    def get_context_data(self, **kwargs):
        context = super(SizeSelectUpdateView, self).get_context_data(**kwargs)
        header = "Select which size you want"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class SellerNotesUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Transaction
    fields = ['seller_notes']
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        transaction = get_object_or_404(Transaction, id=self.kwargs.get('pk'))
        return True if self.request.user == transaction.seller else False

    def get_context_data(self, **kwargs):
        context = super(SellerNotesUpdateView, self).get_context_data(**kwargs)
        header = "Add note as a seller"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class PurchaserNotesUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Transaction
    fields = ['purchaser_notes']
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        transaction = get_object_or_404(Transaction, id=self.kwargs.get('pk'))
        return True if self.request.user == transaction.purchaser else False

    def get_context_data(self, **kwargs):
        context = super(PurchaserNotesUpdateView, self).get_context_data(**kwargs)
        header = "Add note as a purchaser"
        create = False # If update, false; if create, true
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


def processResults(filter, available):

    if filter == 'all':
        subheading = "All results"
        results = available
        
    elif filter == 'tickets-sports':
        subheading = "Sports tickets"
        results = available.filter(listing_category=subheading)
    elif filter == 'tickets-concerts':
        subheading = "Concert tickets"
        results = available.filter(listing_category=subheading)
    elif filter == 'tickets-local':
        subheading = "Local event tickets"
        results = available.filter(listing_category=subheading)
    elif filter == 'tickets-other':
        subheading = "Other tickets"
        results = available.filter(listing_category=subheading)
    
    elif filter == 'tutoring-arts-humanities':
        subheading = "Tutoring - Arts & Humanities"
        results = available.filter(listing_category=subheading)
    elif filter == 'tutoring-sciences':
        subheading = "Tutoring - Sciences"
        results = available.filter(listing_category=subheading)
    elif filter == 'tutoring-tech':
        subheading = "Tutoring - Programming & Technology"
        results = available.filter(listing_category=subheading)
    elif filter == 'tutoring-business':
        subheading = "Tutoring - Business"
        results = available.filter(listing_category=subheading)
    elif filter == 'tutoring-other':
        subheading = "Tutoring - Business"
        results = available.filter(listing_category=subheading)

    elif filter == 'notes-arts-humanities':
        subheading = "Notes - Arts & Humanities"
        results = available.filter(listing_category=subheading)
    elif filter == 'notes-sciences':
        subheading = "Notes - Sciences"
        results = available.filter(listing_category=subheading)
    elif filter == 'notes-tech':
        subheading = "Notes - Programming & Technology"
        results = available.filter(listing_category=subheading)
    elif filter == 'notes-business':
        subheading = "Notes - Business"
        results = available.filter(listing_category=subheading)
    elif filter == 'notes-other':
        subheading = "Notes - Other"
        results = available.filter(listing_category=subheading)

    elif filter == 'services-interview-prep':
        subheading = "Interview prep"
        results = available.filter(listing_category=subheading)
    elif filter == 'services-resume-help':
        subheading = "Résumé help"
        results = available.filter(listing_category=subheading)
    elif filter == 'services-consulting':
        subheading = "Consulting services"
        results = available.filter(listing_category=subheading)
    elif filter == 'services-programming':
        subheading = "Programming services"
        results = available.filter(listing_category=subheading)
    elif filter == 'services-research':
        subheading = "Research assistance"
        results = available.filter(listing_category=subheading)
    elif filter == 'services-translation':
        subheading = "Translation services"
        results = available.filter(listing_category=subheading)
    elif filter == 'services-other':
        subheading = "Other services"
        results = available.filter(listing_category=subheading)

    elif filter == 'books':
        subheading = "Books"
        results = available.filter(listing_category="Book")
    
    elif filter == 'textbooks':
        subheading = "Textbooks"
        results = available.filter(listing_category="Textbook")
    
    elif filter == 'household':
        subheading = "Household"
        results = available.filter(listing_category=subheading)
    
    # elif filter == 'furniture':
    #     subheading = "Furniture"
    #     results = available.filter(listing_category=subheading)

    # elif filter == 'electronics':
    #     subheading = "Electronics"
    #     results = available.filter(listing_category=subheading)

    elif filter == 'mens-clothing-sweatshirts':
        subheading = "Men's sweatshirts"
        results = available.filter(listing_category=subheading)
    elif filter == 'mens-clothing-jackets':
        subheading = "Men's jackets"
        results = available.filter(listing_category=subheading)
    elif filter == 'mens-clothing-suits':
        subheading = "Men's suits"
        results = available.filter(listing_category=subheading)
    elif filter == 'mens-clothing-formal':
        subheading = "Men's formal wear"
        results = available.filter(listing_category=subheading)
    elif filter == 'mens-clothing-other':
        subheading = "Men's clothing - Other"
        results = available.filter(listing_category=subheading)

    elif filter == 'womens-clothing-sweatshirts':
        subheading = "Women's sweatshirts"
        results = available.filter(listing_category=subheading)
    elif filter == 'womens-clothing-jackets':
        subheading = "Women's jackets"
        results = available.filter(listing_category=subheading)
    elif filter == 'womens-clothing-dresses':
        subheading = "Women's dresses"
        results = available.filter(listing_category=subheading)
    elif filter == 'womens-clothing-formal':
        subheading = "Women's formal wear"
        results = available.filter(listing_category=subheading)
    elif filter == 'womens-clothing-other':
        subheading = "Women's clothing - Other"
        results = available.filter(listing_category=subheading)

    elif filter == 'mens-shoes-basketball':
        subheading = "Men's basketball sneakers"
        results = available.filter(listing_category=subheading)
    elif filter == 'mens-shoes-running':
        subheading = "Men's running sneakers"
        results = available.filter(listing_category=subheading)
    elif filter == 'mens-shoes-casual':
        subheading = "Men's casual sneakers"
        results = available.filter(listing_category=subheading)
    elif filter == 'mens-shoes-formal':
        subheading = "Men's formal wear"
        results = available.filter(listing_category=subheading)
    elif filter == 'mens-shoes-other':
        subheading = "Other men's shoes"
        results = available.filter(listing_category=subheading)

    elif filter == 'womens-shoes-basketball':
        subheading = "Women's basketball sneakers"
        results = available.filter(listing_category=subheading)
    elif filter == 'womens-shoes-running':
        subheading = "Women's running sneakers"
        results = available.filter(listing_category=subheading)
    elif filter == 'womens-shoes-casual':
        subheading = "Women's casual sneakers"
        results = available.filter(listing_category=subheading)
    elif filter == 'womens-shoes-formal':
        subheading = "Women's formal wear"
        results = available.filter(listing_category=subheading)
    elif filter == 'womens-shoes-other':
        subheading = "Other women's shoes"
        results = available.filter(listing_category=subheading) 
    elif filter == 'gift-cards':
        subheading = "Gift cards"
        results = available.filter(listing_category=subheading)
    elif filter == 'other':
        subheading = "Other"
        results = available.filter(listing_category=subheading)

    else:
        subheading = "All results"
        results = available

    results = results.exclude(visibility='Invisible').all().order_by('-date_listed')

    return (results, subheading)

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

        available = (Listing.objects.filter(infinite_copies_available=True) | Listing.objects.filter(quantity_available__gt=0, infinite_copies_available=False)) & Listing.objects.filter(listing_type=VARIABLES.LOOKING_TO_SELL)
        
        (results, subheading) = processResults(filter=self.kwargs.get('filter'), available=available)

        context.update({
            "items": results,
            "subheading": subheading,
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
        requestsToBuy = Listing.objects.filter(listing_type=VARIABLES.LOOKING_TO_BUY)
        (results, subheading) = processResults(filter=self.kwargs.get('filter'), available=requestsToBuy)
        context.update({
            "items": results,
            "subheading": subheading,
            "listings_type": "request-to-buy",
            "main_description": main_description,
            "main_header": main_header,
            "num_results": num_results,
            "header": "Users are looking to buy...",
            "user_has_stripe_account_id": get_object_or_404(Profile, user=self.request.user).stripe_account_id is not None
        })
        return context

    # def get_queryset(self):
    #     results = Listing.objects.filter(listing_type=VARIABLES.LOOKING_TO_BUY)
    #     return results.exclude(visibility='Invisible').all().order_by('-date_listed')


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
            message = Mail(from_email=VARIABLES.ADMIN_EMAIL, to_emails=request.user.email, subject=subject, html_content=html_content)
            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            response1 = sg.send(message)
            print(response1)

            # EMAIL TO REQUESTER
            subject = f"Request accepted"
            html_content = f"""
            {current_listing.creator.username} has accepted your request to buy '{current_listing.title}'. You can view this new listing <a href="{BASE_DOMAIN}/market/listing/{new_listing.id}/">here</a>.  
            """
            message = Mail(from_email=VARIABLES.ADMIN_EMAIL, to_emails=request.user.email, subject=subject, html_content=html_content)
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

        clothing = True if listing.listing_category in VARIABLES.CLOTHING_OPTIONS else False

        from users.views import getOverallRating
        overall_rating = getOverallRating(user_being_rated=listing.creator)

        context = {
            "item": listing, 
            "user_is_creator": listing.creator == request.user,
            "obj_type": "listing",
            "all_listings_from_this_creator": all_listings_from_this_creator,

            # "recs": recs,

            "overall_rating": overall_rating,

            "clothing": clothing
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
        success = formValid(user=form.instance.creator, group=form.instance.group)
        print("FORM")
        print(form.instance.pk)
        super().form_valid(form) if success else super().form_invalid(form)
        if success:
            BASE_DOMAIN = getDomain()
            link = f"{BASE_DOMAIN}/market/listing/{form.instance.pk}/"
            description = f"Your listing has been created!!!"
            notified_user = self.request.user
            notification_type = "listing created"
            create_notification(link=link, description=description, notification_type=notification_type, notified_user=notified_user)
        return super().form_valid(form) if success else super().form_invalid(form)


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
        success = formValid(user=form.instance.creator, group=form.instance.group)
        if success:
            BASE_DOMAIN = getDomain()
            link = f"{BASE_DOMAIN}/market/listing/{form.instance.id}/"
            description = f"Your listing has been updated!"
            notified_user = self.request.user
            notification_type = "listing updated"
            create_notification(link=link, description=description, notification_type=notification_type, notified_user=notified_user)
        return super().form_valid(form) if success else super().form_invalid(form)


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
    success_url = '/market/listings/all/'
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


@login_required
def checkout(request, obj_type, pk):
    item = None
    if runningDevServer() or request.user.username in ["baj55", "jad422"]:
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
    # Now we have the item and the user who created the listing.

    if creator_user_profile.stripe_account_id and len(creator_user_profile.stripe_account_id) > 1:
        stripe_account_id = creator_user_profile.stripe_account_id

        if request.user.username == "mbd87":
            commission_fee = 0
        else:
            commission_fee = VARIABLES.COMMISSION_FEE # commission fee
        
        price_rounded = round(item.price, 2)
        total_payment_amount = int(price_rounded * 100)
        payout_amount = int(total_payment_amount - (total_payment_amount * commission_fee))

        if obj_type == VARIABLES.LISTING_OBJ_TYPE:
            market_paymentintent = None
            try:
                market_paymentintent = PaymentIntentTracker.objects.get(
                    user_id=request.user.id, 
                    listing_id=item.id,
                    stripe_account_id=stripe_account_id
                )
            except PaymentIntentTracker.DoesNotExist:
                market_paymentintent = None
        
        elif obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:

            market_paymentintent = None
            try:
                market_paymentintent = PaymentIntentTracker.objects.get(
                    user_id=request.user.id, 
                    listing_for_group_members_id=item.id,
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
            if obj_type == VARIABLES.LISTING_OBJ_TYPE:
                PaymentIntentTracker(
                    stripe_payment_intent_id = payment_intent_id,
                    stripe_account_id = stripe_account_id,
                    listing=item,
                    user_id=request.user.id
                ).save()
                print("CREATEDLISTING")
            elif obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:
                PaymentIntentTracker(
                    stripe_payment_intent_id = payment_intent_id,
                    stripe_account_id = stripe_account_id,
                    listing_for_group_members=item,
                    user_id=request.user.id
                ).save()
                print("CREATEDLISTINGFORGROUPMEMBERS")
            
        # elif obj_type == VARIABLES.LISTING_FOR_GROUP_MEMBERS_OBJ_TYPE:
        #     item = ListingForGroupMembers.objects.get(pk=pk)
        # elif obj_type == VARIABLES.COURSE_OBJ_TYPE:
        #     item = Course.objects.get(pk=pk)
        # elif obj_type == VARIABLES.SPECIALIZATION_OBJ_TYPE:
        #     item = Specialization.objects.get(pk=pk)
        # elif obj_type == VARIABLES.AD_OFFER_OBJ_TYPE:
        #     item = AdOffer.objects.get(pk=pk)
    
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


@login_required
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


@login_required
def payment_cancel(request):
    return render(request, "payments/cancel.html")


def generate_transaction_id(length):
    set_number = '12345678903773764673738299'
    import random
    gen_text = ''.join((random.choice(set_number)) for i in range(length))
    return gen_text


@login_required
def payment_success(request, obj_type, pk):
    clothing = False
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

            if item.listing_category in VARIABLES.CLOTHING_OPTIONS:
                clothing = True

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

            BASE_DOMAIN = getDomain()

            purchaser_link = f"{BASE_DOMAIN}/market/my_purchases/"
            purchaser_description = f"You have purchased '{item.title}'! View all your purchases here."
            purchaser_notified_user = t.purchaser
            purchaser_notification_type = "purchase"
            create_notification(link=purchaser_link, description=purchaser_description, notification_type=purchaser_notification_type, notified_user=purchaser_notified_user)

            seller_link = f"{BASE_DOMAIN}/market/my_sales/"
            seller_description = f"You have sold '{item.title}'! View all your sales here."
            seller_notified_user = t.seller
            seller_notification_type = "sale"
            create_notification(link=seller_link, description=seller_description, notification_type=seller_notification_type, notified_user=seller_notified_user)

            if not t.seller == request.user:
                other_party = t.seller
            elif not t.purchaser == request.user:
                other_party = t.purchaser
            else:
                other_party = None

            print("OP")
            print(other_party)

            return render(request, 'payments/success.html', context={
                "obj_type":  obj_type,
                "session_id": item_id,
                "custom_checkout": is_custom_checkout,
                "other_party": other_party,
                "clothing": clothing,
                "transaction": t
            }) 
        else:
            return render(request, 'payments/cancel.html')
    except Exception as e:
        return render(request, 'payments/cancel.html')


@login_required
def my_payments(request):
    # transaction_verification_data=Transaction.objects.filter(purchaser=request.user,purchaser_verified=None)
    # return render(request,'payments/my_payments.html',{'transaction_verification_data':transaction_verification_data})
    items = list(set(list(Transaction.objects.filter(purchaser=request.user)) + list(Transaction.objects.filter(seller=request.user)))).reverse()
    return render(request,'payments/my_payments.html',{'items': items})


@login_required
def my_purchases(request):
    # transaction_verification_data=Transaction.objects.filter(purchaser=request.user,purchaser_verified=None)
    # return render(request,'payments/my_payments.html',{'transaction_verification_data':transaction_verification_data})
    items = list(Transaction.objects.filter(purchaser=request.user).order_by('-inserted_on'))
    return render(request,'payments/my_purchases_sales.html',{"items": items, "header": "My purchases"})


@login_required
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


def request_payment_from_all_group_members(request, group_id, listing_for_group_members_id):
    (group, group_profile) = get_group_and_group_profile_from_group_id(
        group_id=group_id
    )

    BASE_DOMAIN = getDomain()

    user_sending_request = group_profile.group_creator
    group = Group.objects.get(id=group_id)
    members = group.user_set.all()
    users_receiving_request = []
    for member in members:
        create_payment_request_from_group_member(
            user_sending_request=user_sending_request,
            user_receiving_request=member,
            ListingForGroupMembers_obj_id=listing_for_group_members_id
        ) # Function returns a Bool.
        users_receiving_request.append(member)

        link = f"{BASE_DOMAIN}/market/my/notifications/"
        description = f"{group.name} has requested a payment from you for {listing_for_group_members.title}."
        notified_user = member
        notification_type = "payment request"
        create_notification(link=link, description=description, notification_type=notification_type, notified_user=notified_user)

    listing_for_group_members = get_object_or_404(ListingForGroupMembers, id=listing_for_group_members_id)
    emails_of_users_receiving_request = [u.email for u in users_receiving_request]
    print(emails_of_users_receiving_request)
    try:
        subject = f"Payment request"
        html_content = f"""
        <h3><strong>{group.name} has requested a payment from you for {listing_for_group_members.title}.</strong></h3>
        <h3><strong>Click <a href='{BASE_DOMAIN}/market/checkout/listing_for_group_members/{listing_for_group_members_id}/'>here</a> to pay.</strong></h3>
        <h3><strong>Click <a href='{BASE_DOMAIN}/market/my/notifications/'>here</a> to view all payments requested from you.</strong></h3>
        """
        message = Mail(from_email=VARIABLES.ADMIN_EMAIL, to_emails=emails_of_users_receiving_request, subject=subject, html_content=html_content)
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


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
    BASE_DOMAIN = getDomain()
    try:
        subject = f"Payment request"
        html_content = f"""
        <h3><strong>{group.name} has requested a payment from you for {listing_for_group_members.title}.</strong></h3>
        <h3><strong>Click <a href='{BASE_DOMAIN}/market/checkout/listing_for_group_members/{listing_for_group_members_id}/'>here</a> to pay.</strong></h3>
        <h3><strong>Click <a href='{BASE_DOMAIN}/market/my/notifications/'>here</a> to view all payments requested from you.</strong></h3>
        """
        message = Mail(from_email=VARIABLES.ADMIN_EMAIL, to_emails=user_receiving_request.email, subject=subject, html_content=html_content)
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
    except Exception as e:
        print(e)
    link = f"{BASE_DOMAIN}/market/my/notifications/"
    description = f"{group.name} has requested a payment from you for {listing_for_group_members.title}."
    notified_user = user_receiving_request
    notification_type = "payment request"
    create_notification(link=link, description=description, notification_type=notification_type, notified_user=notified_user)
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
    template_name = 'market/notifications.html'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(RequestForPaymentToGroupMemberListView, self).get_context_data(**kwargs)
        notifications = Notification.objects.filter(notified_user=self.request.user).order_by("-inserted_on").all()
        payment_requests = RequestForPaymentToGroupMember.objects.filter(user_receiving_request=self.request.user).order_by("-inserted_on").all()
        context.update({
            "obj_type": "listing_for_group_members",
            "notifications": notifications,
            "payment_requests": payment_requests,
        })
        return context

    # def get_queryset(self):
    #     reqs = RequestForPaymentToGroupMember.objects.filter(user_receiving_request=self.request.user).all()
    #     return reqs


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
                            message = Mail(from_email=VARIABLES.ADMIN_EMAIL, to_emails=winner.email, subject=subject, html_content=html_content)
                            sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
                            response = sg.send(message)
                            print(response.status_code)
                            print(response.body)
                            print(response.headers)
                        except Exception as e:
                            print(e)
                        link = f"{BASE_DOMAIN}/market/lottery/{lottery.id}/"
                        description = f"You have won a lottery on Hoyabay!"
                        notified_user = winner
                        notification_type = "lottery winner"
                        create_notification(link=link, description=description, notification_type=notification_type, notified_user=notified_user)

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


def ticket_hub_sales(request):
    transactions_where_user_is_seller = Transaction.objects.filter(seller=request.user).filter(transaction_obj_type="listing").all().order_by("-inserted_on")
    ticket_transactions = []
    for t in transactions_where_user_is_seller:
        listing = get_object_or_404(Listing, id=t.transaction_obj_id)
        if listing.listing_category in ["Sports tickets", "Concert tickets", "Local event tickets", "Other tickets"]:
            ticket_transactions.append({"listing": listing, "transaction": t, "other_party": t.purchaser if t.purchaser else None})
    context = {
        "ticket_transactions": ticket_transactions,
        "tab_type": "sales"
    }
    return render(request, 'tickets/ticket_hub.html', context=context)


def ticket_hub_purchases(request):
    transactions_where_user_is_seller = Transaction.objects.filter(purchaser=request.user).filter(transaction_obj_type="listing").all().order_by("-inserted_on")
    ticket_transactions = []
    for t in transactions_where_user_is_seller:
        listing = get_object_or_404(Listing, id=t.transaction_obj_id)
        if listing.listing_category in ["Sports tickets", "Concert tickets", "Local event tickets", "Other tickets"]:
            ticket_transactions.append({"listing": listing, "transaction": t, "other_party": t.seller if t.seller else None})

    context = {
        "ticket_transactions": ticket_transactions,
        "tab_type": "purchases"
    }
    return render(request, 'tickets/ticket_hub.html', context=context)


def requestTicketDigitally(request, transaction_id, listing_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    listing = get_object_or_404(Listing, id=listing_id)


    BASE_DOMAIN = getDomain()
    link = f"{BASE_DOMAIN}/market/ticket/exchange/transaction/{transaction_id}/listing/{listing_id}/"

    description = f"You have requested a digital ticket."
    notified_user = request.user
    notification_type = "ticket request"
    create_notification(link=link, description=description, notification_type=notification_type, notified_user=notified_user)

    description = f"A digital ticket has been requested from you."
    notified_user = transaction.seller
    notification_type = "ticket request"
    create_notification(link=link, description=description, notification_type=notification_type, notified_user=notified_user)

    r = RequestForDigitalTicket(
        user_receiving_request=transaction.seller,
        user_sending_request=request.user,
        transaction=transaction
    )
    r.save()    
    return redirect('ticketPortal', transaction_id=transaction.id, listing_id=listing.id)


def verify_receipt_of_ticket(request, transaction_id, listing_id, party, username):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    listing = get_object_or_404(Listing, id=listing_id)
    if party == "purchaser":
        transaction.purchaser_verified = False if transaction.purchaser_verified else True
        transaction.save()
    else: # party == "seller"
        transaction.seller_verified = False if transaction.seller_verified else True
        transaction.save()
    return redirect('ticketPortal', transaction_id=transaction.id, listing_id=listing.id)


def ticketPortal(request, transaction_id, listing_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    listing = get_object_or_404(Listing, id=listing_id)
    request_exists = False
    if RequestForDigitalTicket.objects.filter(user_receiving_request=transaction.seller, user_sending_request=transaction.purchaser, transaction=transaction).exists():
        request_exists = True
    related_tickets = TicketFile.objects.filter(transaction=transaction).all()
    context = {"transaction": transaction, "listing": listing, "related_tickets": related_tickets, "request_exists": request_exists}
    return render(request, 'tickets/ticket_portal.html', context=context)


class TicketFileCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = TicketFile
    fields = TICKET_FILE_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.transaction = get_object_or_404(Transaction, id=self.kwargs.get('transaction_pk'))
        return super().form_valid(form)

    def test_func(self):
        transaction = get_object_or_404(Transaction, id=self.kwargs.get('transaction_pk'))
        return True if self.request.user == transaction.seller else False

    def get_context_data(self, **kwargs):
        context = super(TicketFileCreateView, self).get_context_data(**kwargs)
        header = "Add ticket"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class TicketFileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TicketFile
    fields = TICKET_FILE_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        transaction = get_object_or_404(Transaction, id=self.kwargs.get('transaction_pk'))
        return True if self.request.user == transaction.seller else False

    def get_context_data(self, **kwargs):
        context = super(TicketFileUpdateView, self).get_context_data(**kwargs)
        header = "Update ticket"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class TicketFileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TicketFile
    success_url = '/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        transaction = get_object_or_404(TicketFile, id=self.kwargs.get('transaction_pk'))
        return self.request.user == transaction.seller

    def get_context_data(self, **kwargs):
        context = super(TicketFileDeleteView, self).get_context_data(**kwargs)
        transaction = get_object_or_404(TicketFile, id=self.kwargs.get('transaction_pk'))
        title = f"Ticket from transaction '{transaction.title}'"
        context.update({"type": "ticket", "title": title})
        return context


def ticketFileDetailView(request, transaction_pk, listing_id, pk):
    transaction = get_object_or_404(Transaction, id=transaction_pk)
    listing = get_object_or_404(Listing, id=listing_id)
    item = get_object_or_404(TicketFile, pk=pk)
    context = {
        "item": item,
        "transaction": transaction,
        "listing": listing
    }
    return render(request, 'tickets/ticket_file_detail_view.html', context)
