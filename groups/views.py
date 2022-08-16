# from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, GroupProfileUpdateForm, GroupUpdateForm

# from django.core.exceptions import PermissionDenied
# from django.contrib.auth.models import User, Group
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# from django.views.generic import (
#     ListView,
#     DetailView,
#     CreateView,
# )


# from .models import GroupProfile, GroupFollowersCount



# class GroupCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):

#     model = Group
#     fields = ['name']
#     template_name = 'malagosto/ecole/FORM_VIEW_BASE.html'#'groups/new_group.html'

#     def form_valid(self, form):
#         # IS THIS THE MOST EFFECTIVE WAY TO REDIRECT?
#         form.save()

#         # Create a new profile upon the creation of a group:
#         new_profile = GroupProfile(group=form.instance)
#         new_profile.save()

#         # UPON CREATE ALSO CREATE A PROFILE FOR THIS GROUP

#         return redirect('group_detail', pk=form.instance.pk) # return super().form_valid(form)

#     def test_func(self):
#         return self.request.user.is_authenticated


# class GroupDetailView(UserPassesTestMixin, DetailView):
#     model = Group

#     def test_func(self):
#         return self.request.user.is_authenticated

#     def get(self, request, *args, **kwargs):
#         group = get_object_or_404(Group, pk=kwargs['pk'])
#         users_in_group = group.user_set.all()
#         logged_in_user_in_group = True if request.user in users_in_group else False

#         logged_in_user = request.user

#         followers_of_group = GroupFollowersCount.objects.filter(group_being_followed=group)
#         num_followers_of_group = len(followers_of_group)
        
#         # user_following = GroupFollowersCount.objects.filter(follower_of_group=user_with_profile_being_viewed)
#         # num_user_following = len(user_following)
        
#         # Who is following the user whose profile we're looking at?
#         # followers_of_user = FollowersCount.objects.filter(user=user_with_profile_being_viewed)
#         # Get data in list:
#         followers_of_group_list = []
#         for user in followers_of_group:
#             followers_of_group_list.append(user.follower_of_group)

#         if logged_in_user in followers_of_group_list:
#             follow_button_val = "Unfollow"
#         else:
#             follow_button_val = "Follow"

#         group_profile = get_object_or_404(GroupProfile, group=group)

#         context = {
#             "item": group,
#             "group_profile": group_profile,
#             "users_in_group": list(users_in_group),
#             "logged_in_user_in_group": logged_in_user_in_group,

#             "follow_button_val": follow_button_val,
#             "num_followers_of_group": num_followers_of_group
#         }
#         return render(request, 'groups/group_detail_view.html', context)


# @login_required
# def group_profile(request, pk):

#     group = get_object_or_404(Group, pk=pk)

#     users_in_group = group.user_set.all()

#     group_profile = get_object_or_404(GroupProfile, group=group)

#     if request.user not in users_in_group:
#         raise PermissionDenied()
#     else:

#         if request.method == 'POST':
#             print(request.POST)
#             p_form = GroupProfileUpdateForm(request.POST,
#                                     request.FILES,
#                                     instance=group_profile)
#             g_form = GroupUpdateForm(request.POST, instance=group)
#             if p_form.is_valid() and g_form.is_valid():
#                 p_form.save()
#                 print("PFORM")
#                 print(p_form)
#                 g_form.save()
#                 messages.success(request, f'Your account has been updated!')
#                 return redirect('group_detail', pk=group.pk)

#         else:
#             p_form = GroupProfileUpdateForm(instance=group_profile)
#             g_form = GroupUpdateForm(instance=group)

#         context = {
#             'item': group,
#             'p_form': p_form,
#             "g_form": g_form,
#             "users_in_group": users_in_group
#         }

#         return render(request, 'groups/group_profile.html', context=context)

# @login_required
# def group_delete(request, pk):

#     group = get_object_or_404(Group, pk=pk)
#     users_in_group = group.user_set.all()

#     group_profile = get_object_or_404(GroupProfile, group=group)

#     print(group)
#     print(group_profile)

#     if request.user not in users_in_group:
#         raise PermissionDenied()
#     else:
#         group.delete()
#         group_profile.delete()
#         return redirect('malagosto_ecole_dashboard')


# class GroupsListView(UserPassesTestMixin, ListView):
#     model = GroupProfile
#     template_name = 'groups/group_list_view.html'
#     context_object_name = 'items'

#     def test_func(self):
#         return self.request.user.is_authenticated

#     def get_context_data(self, **kwargs):
#         context = super(GroupsListView, self).get_context_data(**kwargs)
#         return context

#     # def get_queryset(self):
#     #     return Group.objects.order_by('-name')


# class UserGroupsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
#     model = Group
#     template_name = 'groups/group_list_view.html'
#     context_object_name = 'items'

#     def get_queryset(self):
#         user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
#         items = list(user_in_url.groups.all())
#         return items

#     def get_context_data(self, **kwargs):
#         context = super(UserGroupsListView, self).get_context_data(**kwargs)
#         return context

#     def test_func(self):
#         """
#         user_in_url is the parameter in the URL. Check if this user in URL is same as user logged in.
#         """
#         user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
#         if user_in_url == self.request.user:
#             return True
#         return False


# def group_followers_count(request):
#     if request.method == 'POST':
#         value = request.POST['value']
#         group_name = request.POST['group']
#         group_obj = get_object_or_404(Group, name=group_name)
#         follower_username = request.POST['follower']
#         follower_obj = get_object_or_404(User, username=follower_username)
#         print(f"Group: {group_name}")
#         print(f"Follower: {follower_username}")
#         print(group_obj)
#         print(follower_obj)
#         if value == 'follow':
#             f_cnt = GroupFollowersCount(follower_of_group=follower_obj, group_being_followed=group_obj)
#             f_cnt.save()
#         else:
#             f_cnt = GroupFollowersCount.objects.get(follower_of_group=follower_obj, group_being_followed=group_obj)
#             f_cnt.delete()
#         return redirect('group_detail', pk=group_obj.pk)


