import sys
from decouple import config
import stripe
from numpy import mean
from users.utils import get_user_followers_data
from .forms import ReferralCodeForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import FollowersCount, FollowRequest, Profile, ReferralCode, Rating
from .utils import (
    get_user_followers_data,
    get_groups_that_user_created,
    get_groups_that_user_is_a_member_of,
    get_groups_that_user_follows,
    does_user1_follow_user2
)
from market.models import Transaction
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from config.utils import is_ajax, getOverallRating
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from config.abstract_settings import VARIABLES


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in.')
            user = get_object_or_404(User, username=username)
            profile = get_object_or_404(Profile, user=user)
            profile.credits = 3
            profile.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def user_profile(request, username):
    logged_in_user = request.user
    user_with_profile_being_viewed = get_object_or_404(User, username=username) # User whose profile is being viewed and thus will be followed.

    profile_of_user = get_object_or_404(Profile, user=user_with_profile_being_viewed)

    (list_of_followers, num_followers, users_that_user_with_profile_being_viewed_is_following, num_following) = get_user_followers_data(user_with_profile_being_viewed)

    (group_follows_data, num_groups_that_user_is_following) = get_groups_that_user_follows(user_with_profile_being_viewed)
    (group_member_data, num_groups_that_user_is_a_member_of) = get_groups_that_user_is_a_member_of(user_with_profile_being_viewed)
    (group_creator_data, num_groups_that_user_created) = get_groups_that_user_created(user_with_profile_being_viewed)

    logged_in_user_follows_user_with_profile_being_viewed = does_user1_follow_user2(logged_in_user, user_with_profile_being_viewed) # Does logged in user follow user with profile being viewed?

    numSalesByUser = Transaction.objects.filter(seller=user_with_profile_being_viewed).count()

    logged_in_user_has_bought_from_user_with_profile_being_viewed = Transaction.objects.filter(purchaser=logged_in_user, seller=user_with_profile_being_viewed).exists()

    context = {
        "user_with_profile_being_viewed": user_with_profile_being_viewed,
        "profile_of_user": profile_of_user,
        "logged_in_user": logged_in_user,

        "group_creator_data": group_creator_data, # DONE
        "num_groups_that_user_is_a_member_of": num_groups_that_user_is_a_member_of,

        "group_member_data": group_member_data,
        "num_groups_that_user_created": num_groups_that_user_created,

        "group_follows_data": group_follows_data, 
        "num_groups_that_user_is_following": num_groups_that_user_is_following, 

        "list_of_followers": list_of_followers,
        "num_followers": num_followers,
        "users_that_user_with_profile_being_viewed_is_following": users_that_user_with_profile_being_viewed_is_following,
        "num_following": num_following,

        "logged_in_user_follows_user_with_profile_being_viewed": logged_in_user_follows_user_with_profile_being_viewed,
        "logged_in_user_has_sent_follow_request": FollowRequest.objects.filter(user_requesting_to_follow=logged_in_user, user_receiving_follow_request=user_with_profile_being_viewed).exists(),

        "numSalesByUser": numSalesByUser,

        "logged_in_user_has_bought_from_user_with_profile_being_viewed": logged_in_user_has_bought_from_user_with_profile_being_viewed

    }

    if is_ajax(request=request):
        if request.GET.get('rating'):
            rating = int(request.GET.get('rating'))
            if Rating.objects.filter(rater=logged_in_user, user_being_rated=user_with_profile_being_viewed).exists():
                r = get_object_or_404(Rating, rater=logged_in_user, user_being_rated=user_with_profile_being_viewed)
                r.rating = rating
                r.save()
            else:
                r = Rating(rating=rating, rater=logged_in_user, user_being_rated=user_with_profile_being_viewed)
                r.save()
            overall_rating = getOverallRating(user_being_rated=user_with_profile_being_viewed)
            ratings_dict = {"rating": rating, "overall_rating": overall_rating} # '{0:.1f}'.format(rating)
            return JsonResponse(ratings_dict)

    if Rating.objects.filter(user_being_rated=user_with_profile_being_viewed).exists():
        overall_rating = getOverallRating(user_being_rated=user_with_profile_being_viewed)
        user_has_been_rated = True
    else:
        overall_rating = "NA"
        user_has_been_rated = False
    if Rating.objects.filter(rater=logged_in_user, user_being_rated=user_with_profile_being_viewed).exists():
        rating = get_object_or_404(Rating, rater=logged_in_user, user_being_rated=user_with_profile_being_viewed).rating
        logged_in_user_has_rated = True
    else:
        rating = "NA"
        logged_in_user_has_rated = False
    
    context.update({
        "overall_rating": overall_rating if (isinstance(overall_rating, int) or isinstance(overall_rating, float)) else None,
        "rating": overall_rating if (isinstance(rating, int) or isinstance(rating, float)) else None,
        "user_has_been_rated": user_has_been_rated,
        "logged_in_user_has_rated": logged_in_user_has_rated
    })

    return render(request, 'users/user_profile.html', context)

@login_required
def profile(request):

    current_user = get_object_or_404(User, username=request.user.username)
    profile = get_object_or_404(Profile, user=current_user)
    referral_code = get_object_or_404(ReferralCode, generatedBy=current_user)
    credits = get_object_or_404(Profile, user=request.user).credits

    if profile.stripe_account_id:
        user_has_stripe_connect_account = True
    else:
        user_has_stripe_connect_account = False

    (list_of_followers, num_followers, users_that_user_with_profile_being_viewed_is_following, num_following) = get_user_followers_data(current_user)

    follow_requests = FollowRequest.objects.filter(user_receiving_follow_request=request.user).all()

    (group_follows_data, num_groups_that_user_is_following) = get_groups_that_user_follows(current_user)
    (group_member_data, num_groups_that_user_is_a_member_of) = get_groups_that_user_is_a_member_of(current_user)
    (group_creator_data, num_groups_that_user_created) = get_groups_that_user_created(current_user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    stripe_login_link = None
    try:
        RUNNING_DEVSERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')
        if RUNNING_DEVSERVER:
            stripe.api_key = config('STRIPE_TEST_KEY') 
        else:
            stripe.api_key = config('STRIPE_LIVE_KEY')
        login_link = stripe.Account.create_login_link(request.user.profile.stripe_account_id)
        stripe_login_link = login_link.url + '#/account'
    except:
        print('Stripe account does not exist')
    print(stripe_login_link)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'header': 'My profile',
        'referral_code': referral_code.referral_code,
        "credits": credits,
        'user_has_stripe_connect_account': user_has_stripe_connect_account,

        "group_creator_data": group_creator_data, # DONE
        "num_groups_that_user_is_a_member_of": num_groups_that_user_is_a_member_of,

        "group_member_data": group_member_data,
        "num_groups_that_user_created": num_groups_that_user_created,

        "group_follows_data": group_follows_data, 
        "num_groups_that_user_is_following": num_groups_that_user_is_following, 

        "list_of_followers": list_of_followers,
        "num_followers": num_followers,
        "users_that_user_with_profile_being_viewed_is_following": users_that_user_with_profile_being_viewed_is_following,
        "num_following": num_following,
        "follow_requests": follow_requests,

        'stripe_login_link': stripe_login_link
    }

    return render(request, 'users/profile.html', context)

@login_required
def profileConnectToStripe(request):    
    RUNNING_DEVSERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')

    if RUNNING_DEVSERVER:
        BASE_DOMAIN = 'http://127.0.0.1:8000' 
        stripe.api_key = config('STRIPE_TEST_KEY') 
    else:
        BASE_DOMAIN = 'https://www.hoyabay.com'
        stripe.api_key = config('STRIPE_LIVE_KEY')

    stripeAccount = stripe.Account.create(
        type="express",
        country="US",
        email=request.user.email,
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        },
    )

    accountLinks = stripe.AccountLink.create(
        account=stripeAccount.id,
        refresh_url= BASE_DOMAIN + "/profile",
        return_url= BASE_DOMAIN + "/profile/stripe-connect-callback/" + stripeAccount.id,
        type="account_onboarding",
    )

    return redirect(accountLinks.url)


@login_required
def profileStripeConnectCallback(request, stripe_account_id):
    user_profile = get_object_or_404(Profile, user=request.user)
    user_profile.stripe_account_id = stripe_account_id
    user_profile.save()

    return profile(request)


@login_required
def referral(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.hasUsedAReferralCode:
        messages.success(request, f'You have already used a referral code.')
        return redirect('profile')
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ReferralCodeForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            # process the data in form.cleaned_data as required
            referralEntered = form.cleaned_data.get('referral_code')

            # Check whether referralEntered exists as a referral code:
            referralExists = True if ReferralCode.objects.filter(referral_code=referralEntered) else False

            if referralExists:

                referralObj = ReferralCode.objects.filter(referral_code=referralEntered).first() # Object

                # If referralEntered is the user's own code, then it is invalid.
                if referralObj.generatedBy == request.user: # If the user who generated the referral code is also the user trying to enter the code, then it is invalid.
                    messages.success(request, f'You cannot use your own referral code.')
                    return redirect('profile')

                # If user has already used this code, then it is invalid for them.
                if request.user in referralObj.usedBy.all():
                    messages.success(request, f'You have already used this referral code and cannot do so again.')
                    return redirect('profile')
                
                numTimesUsed = referralObj.usedBy.all().count() # Count how many times it has been used the ManyToMany field.
                MAX_REFERRAL_USES = VARIABLES.MAX_REFERRAL_USES

                if numTimesUsed < MAX_REFERRAL_USES: # Valid; uses have not been used up.
                    NUM_CREDITS_TO_ADD = VARIABLES.NUM_CREDITS_TO_ADD_FOR_REFERRAL
                    messages.success(request, f'That referral code from {referralObj.generatedBy} is valid and has been applied! You and {referralObj.generatedBy} have each received {NUM_CREDITS_TO_ADD} tokens.')
                    # Add 3 credits to both accounts
                    profileOfUserWhoGeneratedCode = get_object_or_404(Profile, user=referralObj.generatedBy)
                    profileOfUserWhoGeneratedCode.credits += NUM_CREDITS_TO_ADD
                    profileOfUserWhoGeneratedCode.save()
                    if True:
                        profileOfUserWhoUsedCode = get_object_or_404(Profile, user=request.user)
                        profile.credits = int(profile.credits) + NUM_CREDITS_TO_ADD
                    # Modify referralObj field 
                    # Save request.user as usedBy
                    referralObj.usedBy.add(request.user)
                    referralObj.save()
                    # hasUsedAReferralCode is set to True in profile model
                    profile.hasUsedAReferralCode = True
                    profile.save()
                else: # Invalid
                    messages.success(request, f'That referral has already been used the maximum number of times allowed and is thus expired.') 
            else:
                messages.warning(request, f'That referral does not exist.')
            return redirect('profile')
    # if a GET (or any other method) we'll create a blank form
    else:
        form = ReferralCodeForm()

    return render(request, 'referral_code.html', {'form': form})


@login_required
def followers_count(request):
    if request.method == 'POST':
        value = request.POST['value']
        user_username = request.POST['user']
        user_obj = get_object_or_404(User, username=user_username)
        follower_username = request.POST['follower']
        follower_obj = get_object_or_404(User, username=follower_username)
        print(f"User: {user_username}")
        print(f"Follower: {follower_username}")
        print(user_obj)
        print(follower_obj)
        if value == 'follow':
            f_cnt = FollowersCount(follower_of_user=follower_obj, user_being_followed=user_obj)
            f_cnt.save()
        else:
            f_cnt = FollowersCount.objects.get(follower_of_user=follower_obj, user_being_followed=user_obj)
            f_cnt.delete()
        return redirect(f'/profile/{user_username}')


@login_required
def follow_request(request, user_requesting_to_follow, user_receiving_follow_request):
    user_requesting_to_follow = get_object_or_404(User, username=user_requesting_to_follow)
    user_receiving_follow_request = get_object_or_404(User, username=user_receiving_follow_request)
    
    requesting_user_follows_user_with_profile_being_viewed = does_user1_follow_user2(user_requesting_to_follow, user_receiving_follow_request)
    
    # Check if FollowRequest doesn't yet exist
    if not requesting_user_follows_user_with_profile_being_viewed and not FollowRequest.objects.filter(user_requesting_to_follow=user_requesting_to_follow, user_receiving_follow_request=user_receiving_follow_request).exists():
        follow_request = FollowRequest(user_requesting_to_follow=user_requesting_to_follow, user_receiving_follow_request=user_receiving_follow_request)
        follow_request.save()
    return redirect(f'/profile/{user_receiving_follow_request}')


def delete_follow_request(user_requesting_to_follow, user_receiving_follow_request):
    # Check if follower request exists. If it does, delete that object.
    if FollowRequest.objects.filter(user_requesting_to_follow=user_requesting_to_follow, user_receiving_follow_request=user_receiving_follow_request).exists():
        follow_request = get_object_or_404(FollowRequest, user_requesting_to_follow=user_requesting_to_follow, user_receiving_follow_request=user_receiving_follow_request)
        follow_request.delete()


@login_required
def withdraw_follow_request(request, user_requesting_to_follow, user_receiving_follow_request):
    user_requesting_to_follow = get_object_or_404(User, username=user_requesting_to_follow)
    user_receiving_follow_request = get_object_or_404(User, username=user_receiving_follow_request)
    delete_follow_request(user_requesting_to_follow, user_receiving_follow_request)
    return redirect(f'/profile/{user_receiving_follow_request}')


@login_required
def accept_follow_request(request, user_requesting_to_follow, user_receiving_follow_request):
    user_requesting_to_follow = get_object_or_404(User, username=user_requesting_to_follow)
    user_receiving_follow_request = get_object_or_404(User, username=user_receiving_follow_request)
    new_follower_obj = FollowersCount(follower_of_user=user_requesting_to_follow, user_being_followed=user_receiving_follow_request)
    new_follower_obj.save()
    delete_follow_request(user_requesting_to_follow, request.user)
    return redirect('profile')


@user_passes_test(lambda u: u.is_superuser and u.username == "bml74")
def admin_dashboard(request):
    users = User.objects.all()
    transactions = Transaction.objects.all()
    amount_to_stripe = 0
    for tr in transactions:
        to_stripe = .3
        leftover = tr.value - to_stripe
        to_stripe += leftover * .029
        amount_to_stripe += to_stripe
    sold_by_bml74 = Transaction.objects.filter(seller=request.user.id).all()
    print("ljknihuygtfrdhfyghukj")
    print(mean([t.value for t in sold_by_bml74]))
    context = {
        "num_users": len(users),
        "num_transactions": len(transactions),
        "avg_transaction_amount": mean([t.value for t in transactions]),
        "gmv": sum([t.value for t in transactions]),

        "avg_transaction_amount_for_bml74": mean([t.value for t in sold_by_bml74]),
        "gmv_for_bml74": sum([t.value for t in sold_by_bml74]),

        "amount_to_stripe": amount_to_stripe
        
    }
    return render(request, 'users/admin_dashboard.html', context=context)