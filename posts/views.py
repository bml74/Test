from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.models import User, Group
from orgs.models import GroupProfile
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Post
from ecoles.datatools import generate_recommendations_from_queryset


class PostListView(ListView):
    """
    Displays all posts by anyone.
    Work on this. Goal is to make it so that after posts can be either
    public or private, it will only display public posts.
    """
    model = Post
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context.update({"header": "Posts", "title": "Posts", "type": "post"})
        return context


class UserPostListView(ListView):
    """
    Displays all posts by specific user as specified in URL.
    Work on this. Goal is to make it so that after posts can be either
    public or private, it will only display public posts by the user.
    """
    model = Post
    template_name = 'finance/finance_list_view.html'
    context_object_name = 'items'
    paginate_by = 10

    def get_queryset(self):
        """Get posts by specific user (as passed into URL)."""
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        context = super(UserPostListView, self).get_context_data(**kwargs)
        username=self.kwargs.get('username')
        context.update({"header": f"Posts by {username}", "title": f"Posts by {username}", "type": "post"})
        return context


class PostDetailView(UserPassesTestMixin, DetailView):
    model = Post
    template_name = 'posts/post_detail_view.html'
    context_object_name = 'item'

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        recs = generate_recommendations_from_queryset(queryset=Post.objects.all(), obj=post)
        context = {
            "recs": recs
        }
        return render(request, 'market/COURSE_DESIGN.html', context)


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    fields = ['title', 'group', 'content']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
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
        context = super(PostCreateView, self).get_context_data(**kwargs)
        header = "Create post"
        create = True # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'group', 'content']
    template_name = 'views/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
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
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(PostUpdateView, self).get_context_data(**kwargs)
        header = "Update post"
        create = False # If update, false; if create, true
        context.update({"header": header, "create": create})
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete post."""
    model = Post
    success_url = '/'
    context_object_name = 'item'
    template_name = 'views/confirm_delete.html'

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_context_data(self, **kwargs):
        context = super(PostDeleteView, self).get_context_data(**kwargs)
        transaction = get_object_or_404(Post, id=self.kwargs.get('pk'))
        title = f"Post: {transaction.title}"
        context.update({"type": "post", "title": title})
        return context


# @login_required
# def favorite_post(request, pk):
#     """favorite an article."""
#     post = get_object_or_404(Post, id=pk)
#     if post.favorited_by.filter(id=request.user.id).exists():
#         post.favorited_by.remove(request.user)
#     else:
#         post.favorited_by.add(request.user)
#     return HttpResponseRedirect(request.META['HTTP_REFERER'])


# class Favorites(LoginRequiredMixin, TemplateView):
#     template_name = 'blog/favorites.html'

