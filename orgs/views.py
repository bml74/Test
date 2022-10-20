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

from .models import GroupProfile



class GroupCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

    model = Group
    fields = ['name']
    template_name = 'market/dashboard/form_view.html'#'groups/new_group.html'

    def form_valid(self, form):
        # IS THIS THE MOST EFFECTIVE WAY TO REDIRECT?
        form.save()

        # Create a new profile upon the creation of a group:
        new_profile = GroupProfile(group=form.instance)
        new_profile.save()

        # UPON CREATE ALSO CREATE A PROFILE FOR THIS GROUP

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

            # "follow_button_val": follow_button_val,
            # "num_followers_of_group": num_followers_of_group
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

    # def get_queryset(self):
    #     return Group.objects.order_by('-name')


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
    group = get_object_or_404(Group, pk=pk)
    obj = get_object_or_404(GroupProfile, group=group)
    if obj.group_followers.filter(id=request.user.id).exists():
        obj.group_followers.remove(request.user)
    else:
        obj.group_followers.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


