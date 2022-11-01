from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.models import User
from .models import (
    Category, 
    Field
)
from .datatools import generate_recommendations_from_queryset
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['title', 'description', 'creator']
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(CategoryCreateView, self).get_context_data(**kwargs)
        header = "Create category"
        context.update({"header": header})
        context.update({"obj_type": "category"})
        return context


class CategoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Category
    fields = ['title', 'description', 'creator']
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user enrolled in the course.
        category = Category.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == category.creator or self.request.user in category.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(CategoryUpdateView, self).get_context_data(**kwargs)
        header = "Update category"
        context.update({"header": header})
        context.update({"obj_type": "category"})
        return context


class CategoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Category
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = 'ecoles/confirm_delete_view.html'

    def test_func(self):
        # Check if user enrolled in the course.
        category = Category.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == category.creator

    def get_context_data(self, **kwargs):
        context = super(CategoryDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": "category"})
        return context


class CategoryDetailView(UserPassesTestMixin, DetailView):
    model = Category

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        obj_type = "category"
        category = get_object_or_404(Category, pk=kwargs['pk'])
        user_enrolled = request.user in category.students.all()
        allowed_to_edit = request.user in category.allowed_editors.all()
        user_is_creator = request.user == category.creator
        request_already_sent = request.user in category.edit_access_request.all()
        fields = Field.objects.filter(category=category)

        users_with_requests = category.edit_access_request.all()
        users_with_edit_access = category.allowed_editors.all()

        recs = generate_recommendations_from_queryset(queryset=Category.objects.all(), obj=category)
        print(recs)

        context = {
            "obj_type": obj_type, 
            "item": category, 
            "category": category, 
            "user_enrolled": user_enrolled,
            "allowed_to_edit": allowed_to_edit,
            "user_is_creator": user_is_creator,
            "request_already_sent": request_already_sent,
            "users_with_requests": users_with_requests,
            "users_with_edit_access": users_with_edit_access,

            "fields": fields,

            "recs": recs

        }
        return render(request, 'ecoles/category_and_field_detail_view_base.html', context)


class CategoryListView(UserPassesTestMixin, ListView):
    model = Category
    template_name = 'ecoles/category_and_field_list_view_base.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        title = "Categories"
        header = "View all categories"
        context.update({"title": title, "header": header})
        context.update({"obj_type": "category"})
        return context

    def get_queryset(self):
        return Category.objects.order_by('-title')


class EnrolledCategoriesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'ecoles/category_and_field_list_view_base.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Category.objects.filter(students=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(EnrolledCategoriesListView, self).get_context_data(**kwargs)
        title = "Enrolled | Categories"
        header = "Categories I'm enrolled in"
        context.update({"title": title, "header": header})
        context.update({"obj_type": "category"})
        return context

    def test_func(self):
        """
        user_in_url is the parameter in the URL. Check if this user in URL is same as user logged in.
        """
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        if user_in_url == self.request.user:
            return True
        return False


class CreatedCategoriesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'ecoles/category_and_field_list_view_base.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Category.objects.filter(creator=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(CreatedCategoriesListView, self).get_context_data(**kwargs)
        title = "Categories created by " + self.kwargs.get('username')
        header = "Categories created by " + self.kwargs.get('username')
        context.update({"title": title, "header": header})
        context.update({"obj_type": "category"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class EditAccessCategoriesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Category
    template_name = 'ecoles/category_and_field_list_view_base.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        created = list(Category.objects.filter(creator=user_in_url))
        items = list(user_in_url.category_allowed_editors.all()) + created
        return items

    def get_context_data(self, **kwargs):
        context = super(EditAccessCategoriesListView, self).get_context_data(**kwargs)
        title = "Edit Access | Categories"
        header = "Categories I Can Edit"
        context.update({"title": title, "header": header})
        context.update({"obj_type": "category"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user

