from requests import request
from .forms import GroupProfileUpdateForm, GroupUpdateForm

from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)
from market.models import Listing
from ecoles.models import Specialization, Course
from posts.models import Post
from .models import GroupProfile, GroupFollowRequest, GroupMembershipRequest
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME
from config.utils import get_group_and_group_profile_from_group_id


class GroupCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = Group
    fields = ['name']
    template_name = FORM_VIEW_TEMPLATE_NAME#'groups/new_group.html'

    def get_context_data(self, **kwargs):
        context = super(GroupCreateView, self).get_context_data(**kwargs)
        obj_type = "group"
        context.update({"obj_type": obj_type, "header": f"Create {obj_type}"})
        return context

    def form_valid(self, form):
        form.save()
        # Create a new profile upon the creation of a group:
        new_profile = GroupProfile(group=form.instance)
        new_profile.save()
        # Add user as group_member to group profile
        new_profile.group_creator = self.request.user
        new_profile.group_members.add(self.request.user)
        new_profile.group_followers.add(self.request.user)
        new_profile.save()
        # Add user as group member to built-in Django groups
        form.instance.user_set.add(self.request.user)
        return redirect('group_detail', pk=form.instance.pk) # return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated


class GroupDetailView(UserPassesTestMixin, DetailView):
    model = Group

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group, pk=kwargs['pk'])
        users_in_group = group.user_set.all()
        logged_in_user_in_group = True if request.user in users_in_group else False

        # followers_of_group = GroupFollowersCount.objects.filter(group_being_followed=group)
        # num_followers_of_group = len(followers_of_group)
        
        # # user_following = GroupFollowersCount.objects.filter(follower_of_group=user_with_profile_being_viewed)
        # # num_user_following = len(user_following)
        
        # # Who is following the user whose profile we're looking at?
        # # followers_of_user = FollowersCount.objects.filter(user=user_with_profile_being_viewed)
        # # Get data in list:
        # followers_of_group_list = []
        # for user in followers_of_group:
        #     followers_of_group_list.append(user.follower_of_group)

        # if logged_in_user in followers_of_group_list:
        #     follow_button_val = "Unfollow"
        # else:
        #     follow_button_val = "Follow"

        group_profile = get_object_or_404(GroupProfile, group=group)

        listings = Listing.objects.filter(group=group)
        if len(listings) > 10:
            listings = listings[:10]
        courses = Course.objects.filter(group=group)
        if len(courses) > 10:
            courses = courses[:10]
        specializations = Specialization.objects.filter(group=group)
        if len(specializations) > 10:
            specializations = specializations[:10]
        news = Post.objects.filter(group=group)
        if len(news) > 10:
            news = news[:10]

        context = {
            "obj_type": "group",
            "item": group_profile,
            "group_profile": group_profile,
            "users_in_group": list(users_in_group),
            "logged_in_user_in_group": logged_in_user_in_group,
            "user_is_creator": group_profile.group_creator == request.user,
            "user_follows_this_group": group_profile.group_followers.filter(id=request.user.id).exists(),

            "first_few_listings": listings,
            "first_few_courses": courses,
            "first_few_specializations": specializations,
            "first_few_news": news,

            "user_has_made_membership_request": GroupMembershipRequest.objects.filter(user_requesting_to_become_member=request.user, group_receiving_membership_request=group).exists(),
            "membership_requests": GroupMembershipRequest.objects.all()

        }

        return render(request, 'groups/group_detail_view.html', context)


@login_required
def group_profile(request, pk):

    group = get_object_or_404(Group, pk=pk)

    users_in_group = group.user_set.all()

    group_profile = get_object_or_404(GroupProfile, group=group)

    if request.user not in users_in_group:
        raise PermissionDenied()
    else:

        if request.method == 'POST':
            print(request.POST)
            p_form = GroupProfileUpdateForm(request.POST,
                                    request.FILES,
                                    instance=group_profile)
            g_form = GroupUpdateForm(request.POST, instance=group)
            if p_form.is_valid() and g_form.is_valid():
                p_form.save()
                print("PFORM")
                print(p_form)
                g_form.save()
                messages.success(request, f'Your account has been updated!')
                return redirect('group_detail', pk=group.pk)

        else:
            p_form = GroupProfileUpdateForm(instance=group_profile)
            g_form = GroupUpdateForm(instance=group)

        context = {
            'item': group,
            'p_form': p_form,
            "g_form": g_form,
            "users_in_group": users_in_group
        }

        return render(request, 'groups/group_profile.html', context=context)


@login_required
def group_delete(request, pk):

    group = get_object_or_404(Group, pk=pk)
    users_in_group = group.user_set.all()

    group_profile = get_object_or_404(GroupProfile, group=group)

    print(group)
    print(group_profile)

    if request.user not in users_in_group:
        raise PermissionDenied()
    else:
        group.delete()
        group_profile.delete()
        return redirect('groups_list_view')


class GroupsListView(UserPassesTestMixin, ListView):
    model = GroupProfile
    template_name = 'groups/group_list_view.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(GroupsListView, self).get_context_data(**kwargs)
        context.update({
            "obj_type": "group",
            "num_results": len(Group.objects.all())
        })
        return context

    def get_queryset(self):
        return Group.objects.order_by('-name')


class UserGroupsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Group
    template_name = 'groups/group_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(user_in_url.groups.all())
        return items

    def get_context_data(self, **kwargs):
        context = super(UserGroupsListView, self).get_context_data(**kwargs)
        context.update({
            "obj_type": "group",
            "num_results": len(Group.objects.all())
        })
        return context

    def test_func(self):
        """
        user_in_url is the parameter in the URL. Check if this user in URL is same as user logged in.
        """
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        if user_in_url == self.request.user:
            return True
        return False


@login_required
def follow_group(request, pk):
    (group, group_profile) = get_group_and_group_profile_from_group_id(group_id=pk)
    if group_profile.group_followers.filter(id=request.user.id).exists():
        group_profile.group_followers.remove(request.user)
    else:
        group_profile.group_followers.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def group_membership(request, username, pk):
    (group, group_profile) = get_group_and_group_profile_from_group_id(group_id=pk)
    user = get_object_or_404(User, username=username)
    if group_profile.group_members.filter(id=user.id).exists():
        group_profile.group_members.remove(user)
        group.user_set.remove(user)
    else:
        group_profile.group_members.add(user)
        group.user_set.add(user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


# Membership request: Create membership request object
@login_required
def request_membership(request, group_id):
    (group_receiving_request, group_profile) = get_group_and_group_profile_from_group_id(group_id)
    # Boolean filters:
    user_is_member = request.user in group_profile.group_members.all()
    request_exists = GroupMembershipRequest.objects.filter(user_requesting_to_become_member=request.user, group_receiving_membership_request=group_receiving_request).exists()
    # If user is not a member and user has not made a request for this group so far, create request and save.
    if not user_is_member and not request_exists:
        group_request = GroupMembershipRequest(user_requesting_to_become_member=request.user, group_receiving_membership_request=group_receiving_request)
        group_request.save()
    return redirect('group_detail', pk=group_id)


def delete_membership_request(username, group_receiving_request):
    user = get_object_or_404(User, username=username)
    membership_request = get_object_or_404(GroupMembershipRequest, user_requesting_to_become_member=user, group_receiving_membership_request=group_receiving_request)
    membership_request.delete()


# Withdraw membership request: Delete membership request object
@login_required
def withdraw_membership_request(request, username, group_id):
    (group_receiving_request, group_profile) = get_group_and_group_profile_from_group_id(group_id)
    user = get_object_or_404(User, username=username)
    user_is_member = user in group_profile.group_members.all()
    request_exists = GroupMembershipRequest.objects.filter(user_requesting_to_become_member=user, group_receiving_membership_request=group_receiving_request).exists()
    # If user is not a member and user has not made a request for this group so far, create request and save.
    if not user_is_member and request_exists:
        delete_membership_request(username, group_receiving_request)
    return redirect('group_detail', pk=group_id)


# Accept memebrship request: Add to MTM field and delete membership request object
@login_required
def accept_membership_request(request, username, group_id):
    (group_receiving_request, group_profile) = get_group_and_group_profile_from_group_id(group_id)
    # Add membership
    group_membership(request, username, group_id)
    delete_membership_request(username, group_receiving_request)
    return redirect('group_detail', pk=group_id)


# Follow request: Create follow request object

# Delete follow request

# Withdraw follow request: Delete follow request object

# Accept follow request: Add to MTM field and delete follow request object


# NOTE: MAKE SURE THAT ONLY THOSE WHO CAN ACCEPT OR REJECT REQUESTS ARE GROUP CREATORS.