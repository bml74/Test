from .forms import ReferralCodeForm, UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import FollowersCount, Profile, ReferralCode

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


def user_profile(request, username):
    logged_in_user = request.user
    user_with_profile_being_viewed = get_object_or_404(User, username=username) # User whose profile is being viewed and thus will be followed.

    profile_of_user = get_object_or_404(Profile, user=user_with_profile_being_viewed)

    list_of_followers = FollowersCount.objects.filter(user_being_followed=user_with_profile_being_viewed).all()
    num_followers = len(list_of_followers)

    users_that_user_with_profile_being_viewed_is_following = FollowersCount.objects.filter(follower_of_user=user_with_profile_being_viewed).all()
    num_following = len(users_that_user_with_profile_being_viewed_is_following)

    context = {
        "user_with_profile_being_viewed": user_with_profile_being_viewed,
        "profile_of_user": profile_of_user,
        "logged_in_user": logged_in_user,

        "list_of_followers": list_of_followers,
        "num_followers": num_followers,
        "users_that_user_with_profile_being_viewed_is_following": users_that_user_with_profile_being_viewed_is_following,
        "num_following": num_following
    }
    return render(request, 'users/user_profile.html', context)


@login_required
def profile(request):

    current_user = get_object_or_404(User, username=request.user.username)
    referral_code = get_object_or_404(ReferralCode, generatedBy=current_user)


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

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'header': 'My profile',
        'referral_code': referral_code.referral_code,
    }

    return render(request, 'users/profile.html', context)


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
                MAX_REFERRAL_USES = 5

                if numTimesUsed < MAX_REFERRAL_USES: # Valid; uses have not been used up.
                    NUM_CREDITS_TO_ADD = 100
                    messages.success(request, f'That referral code from {referralObj.generatedBy} is valid and has been applied! You and {referralObj.generatedBy} have each received {NUM_CREDITS_TO_ADD} tokens.')
                    # Add 100 tokens to both accounts
                    profileOfUserWhoGeneratedCode = get_object_or_404(Profile, user=referralObj.generatedBy)
                    profileOfUserWhoGeneratedCode.credits += 100; profileOfUserWhoGeneratedCode.save()
                    profileOfUserWhoUsedCode = get_object_or_404(Profile, user=request.user)
                    profileOfUserWhoUsedCode.credits += 100; profileOfUserWhoUsedCode.save()
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

