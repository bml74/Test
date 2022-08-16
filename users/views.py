from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import FollowersCount

from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
    context = {
        "user_with_profile_being_viewed": user_with_profile_being_viewed,
        "logged_in_user": logged_in_user,
    }
    return render(request, 'users/user_profile.html', context)


@login_required
def profile(request):

    current_user = get_object_or_404(User, username=request.user.username)


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
    }

    return render(request, 'users/profile.html', context)


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

