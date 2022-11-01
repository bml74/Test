from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import (
    Category, 
    Field, 
    Specialization,
    Course
)
from django.contrib.auth.models import User
from .datatools import generate_recommendations_from_queryset
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME
from config.abstract_settings.model_fields import FIELD_FIELDS


class FieldCreateView(LoginRequiredMixin, CreateView):
    model = Field
    fields = FIELD_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(FieldCreateView, self).get_context_data(**kwargs)
        header = "Create field"
        context.update({"header": header})
        context.update({"obj_type": "field"})
        return context


class FieldUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Field
    fields = FIELD_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user enrolled in the course.
        field = Field.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == field.creator or self.request.user in field.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(FieldUpdateView, self).get_context_data(**kwargs)
        header = "Update field"
        context.update({"header": header})
        context.update({"obj_type": "field"})
        return context


class FieldDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Field
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        # Check if user enrolled in the course.
        field = Field.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == field.creator

    def get_context_data(self, **kwargs):
        context = super(FieldDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": "field"})
        return context


class FieldDetailView(UserPassesTestMixin, DetailView):
    model = Field

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        obj_type = "field"
        field = get_object_or_404(Field, pk=kwargs['pk'])
        user_enrolled = request.user in field.students.all() 
        allowed_to_edit = request.user in field.allowed_editors.all()
        category = get_object_or_404(Category, pk=field.category.id)
        courses = Course.objects.filter(field=field)
        specializations = Specialization.objects.filter(field=field)

        user_is_creator = request.user == field.creator
        request_already_sent = request.user in field.edit_access_request.all()
        users_with_requests = field.edit_access_request.all()
        users_with_edit_access = field.allowed_editors.all()

        recs = generate_recommendations_from_queryset(queryset=Field.objects.all(), obj=field)
        print(recs)

        context = {
            "obj_type": obj_type, 
            "item": field, 
            "field": field, 
            "user_enrolled": user_enrolled,
            "allowed_to_edit": allowed_to_edit,
            "user_is_creator": user_is_creator,
            "request_already_sent": request_already_sent,
            "users_with_requests": users_with_requests,
            "users_with_edit_access": users_with_edit_access,

            "category": category, 
            "specializations": specializations,
            "courses": courses,

            "recs": recs

        }
        return render(request, 'ecoles/category_and_field_detail_view_base.html', context)



class FieldListView(UserPassesTestMixin, ListView):
    model = Field
    template_name = 'ecoles/category_and_field_list_view_base.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(FieldListView, self).get_context_data(**kwargs)
        title = "Fields"
        header = "View all fields"
        context.update({"title": title, "header": header})
        context.update({"obj_type": "field"})
        return context

    def get_queryset(self):
        return Field.objects.order_by('-title')


class EnrolledFieldsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Field
    template_name = 'ecoles/category_and_field_list_view_base.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Field.objects.filter(students=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(EnrolledFieldsListView, self).get_context_data(**kwargs)
        title = "Enrolled | Fields"
        header = "Fields I'm enrolled in"
        context.update({"title": title, "header": header})
        context.update({"obj_type": "field"})
        return context

    def test_func(self):
        """
        user_in_url is the parameter in the URL. Check if this user in URL is same as user logged in.
        """
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        if user_in_url == self.request.user:
            return True
        return False


class CreatedFieldsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Field
    template_name = 'ecoles/category_and_field_list_view_base.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Field.objects.filter(creator=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(CreatedFieldsListView, self).get_context_data(**kwargs)
        title = "Fields created by " + self.kwargs.get('username')
        header = "Fields created by " + self.kwargs.get('username')
        context.update({"title": title, "header": header})
        context.update({"obj_type": "field"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class EditAccessFieldsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Field
    template_name = 'ecoles/category_and_field_list_view_base.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        created = list(Field.objects.filter(creator=user_in_url))
        items = list(user_in_url.field_allowed_editors.all()) + created
        return items

    def get_context_data(self, **kwargs):
        context = super(EditAccessFieldsListView, self).get_context_data(**kwargs)
        title = "Edit Access | Fields"
        header = "Fields I Can Edit"
        context.update({"title": title, "header": header})
        context.update({"obj_type": "field"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user

