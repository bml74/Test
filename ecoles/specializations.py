from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
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
    Field, 
    Specialization,
    Course,
    Module, 
    Submodule, 
    Assignment,
    Task,
)
from .models import Ecole


class SpecializationListView(UserPassesTestMixin, ListView):
    model = Specialization
    template_name = 'ecoles/specialization_and_course_list_view.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(SpecializationListView, self).get_context_data(**kwargs)
        obj_type = "specialization"
        context.update({"obj_type": obj_type, "header": f"{obj_type.capitalize()}s", "title": f"{obj_type.capitalize()}s"})
        return context

    def get_queryset(self):
        return Specialization.objects.order_by('-title')


class EnrolledSpecializationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Specialization
    template_name = 'ecoles/specialization_and_course_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Specialization.objects.filter(students=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(EnrolledSpecializationsListView, self).get_context_data(**kwargs)
        obj_type = "specialization"
        context.update({"obj_type": obj_type, "header": f"{obj_type.capitalize()}s I'm enrolled in", "title": f"Enrolled | {obj_type.capitalize()}s"})
        return context

    def test_func(self):
        """
        user_in_url is the parameter in the URL. Check if this user in URL is same as user logged in.
        """
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        if user_in_url == self.request.user:
            return True
        return False


class CreatedSpecializationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Specialization
    template_name = 'ecoles/specialization_and_course_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Specialization.objects.filter(creator=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(CreatedSpecializationsListView, self).get_context_data(**kwargs)
        obj_type = "specialization"
        context.update({"obj_type": obj_type, "header": f"{obj_type.capitalize()}s I've created", "title": f"My Creations | {obj_type.capitalize()}"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class EditAccessSpecializationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Specialization
    template_name = 'ecoles/specialization_and_course_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        created = list(Specialization.objects.filter(creator=user_in_url))
        items = list(user_in_url.specialization_allowed_editors.all()) + created
        return items

    def get_context_data(self, **kwargs):
        context = super(EditAccessSpecializationsListView, self).get_context_data(**kwargs)
        obj_type = "specialization"
        context.update({"obj_type": obj_type, "header": f"{obj_type.capitalize()}s I can edit", "title": f"Edit Access | {obj_type.capitalize()}"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class SpecializationDetailView(UserPassesTestMixin, DetailView):
    model = Specialization

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        obj_type = "specialization"
        specialization = get_object_or_404(Specialization, pk=kwargs['pk'])
        user_enrolled = request.user in specialization.students.all() 
        allowed_to_edit = request.user in specialization.allowed_editors.all()
        try:
            field = get_object_or_404(Field, pk=specialization.field.id)
        except AttributeError: 
            field = None
        try:
            category = get_object_or_404(Category, pk=field.category.id)
        except AttributeError: 
            category = None
        try:
            courses = Course.objects.filter(specialization=specialization)
        except AttributeError:
            courses = None

        user_is_creator = request.user == specialization.creator
        request_already_sent = request.user in specialization.edit_access_request.all()
        users_with_requests = specialization.edit_access_request.all()
        users_with_edit_access = specialization.allowed_editors.all()

        # # Progress bar:
        # total_assignments = 0 # submodules = Submodule.objects.filter(module=module)
        # total_assignments_completed = 0
        # for course in courses:
        #     modules = Module.objects.filter(course=course)
        #     for module in modules:
        #         submodules = Submodule.objects.filter(module=module)
        #         for submodule in submodules:
        #             assignments = Assignment.objects.filter(submodule=submodule)
        #             num_assignments = len(list(Assignment.objects.filter(submodule=submodule)))
        #             total_assignments += num_assignments
        #             num_assignments_completed = 0
        #             for assignment in assignments:
        #                 if request.user in assignment.completed.all():
        #                     num_assignments_completed += 1
        #                     total_assignments_completed += num_assignments_completed
        # try:
        #     pct_completed = int((total_assignments_completed / (total_assignments)) * 100)
        # except ZeroDivisionError:
        #     pct_completed = 0

        context = {
            "obj_type": obj_type, 
            "item": specialization, 
            "specialization": specialization, 
            "user_enrolled": user_enrolled,
            "allowed_to_edit": allowed_to_edit,
            "user_is_creator": user_is_creator,
            "request_already_sent": request_already_sent,
            "users_with_requests": users_with_requests,
            "users_with_edit_access": users_with_edit_access,
            # "pct_completed": pct_completed,

            "category": category, 
            "field": field, 
            "courses": courses,

        }
        return render(request, 'ecoles/specializations/specialization_detail_view.html', context)


class SpecializationCreateView(LoginRequiredMixin, CreateView):
    model = Specialization
    fields = ['title', 'field', 'visibility', 'description', 'difficulty_level', 'creator']
    template_name = 'ecoles/ecoles_form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(SpecializationCreateView, self).get_context_data(**kwargs)
        obj_type = "specialization"
        context.update({"obj_type": obj_type, "header": f"Create {obj_type}"})
        return context


class SpecializationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Specialization
    fields = ['title', 'field', 'visibility', 'description', 'difficulty_level', 'creator']
    template_name = 'ecoles/ecoles_form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user enrolled in the course.
        specialization = Specialization.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == specialization.creator

    def get_context_data(self, **kwargs):
        context = super(SpecializationUpdateView, self).get_context_data(**kwargs)
        obj_type = "specialization"
        context.update({"obj_type": obj_type, "header": f"Update {obj_type}"})
        return context


class SpecializationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Specialization
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = 'ecoles/confirm_delete_view.html'

    def test_func(self):
        # Check if user enrolled in the course.
        specialization = Specialization.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == specialization.creator

    def get_context_data(self, **kwargs):
        context = super(SpecializationDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": "specialization"})
        return context



