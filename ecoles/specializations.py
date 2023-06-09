from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.contrib.auth.models import User, Group
from orgs.models import GroupProfile
from .models import (
    Category, 
    Field, 
    Specialization,
    Course
)
from .datatools import generate_recommendations_from_queryset
from config.abstract_settings.model_fields import SPECIALIZATION_FIELDS
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME, ITEM_LIST_TEMPLATE_NAME
from config.utils import formValid


SINGULAR_NAME = "Specialization"
PLURAL_NAME = "Specializations"


class SpecializationListView(UserPassesTestMixin, ListView):
    model = Specialization
    template_name = ITEM_LIST_TEMPLATE_NAME
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(SpecializationListView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        context.update({"obj_type": obj_type, "num_results": len(Specialization.objects.all()), "header": PLURAL_NAME})
        return context

    def get_queryset(self):
        return Specialization.objects.order_by('-title')


class EnrolledSpecializationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Specialization
    template_name = ITEM_LIST_TEMPLATE_NAME
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Specialization.objects.filter(students=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(EnrolledSpecializationsListView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Specialization.objects.filter(students=user_in_url))
        context.update({"obj_type": obj_type, "num_results": len(items), "header": f"{PLURAL_NAME} I'm enrolled in"})
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
    template_name = ITEM_LIST_TEMPLATE_NAME
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Specialization.objects.filter(creator=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(CreatedSpecializationsListView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Specialization.objects.filter(creator=user_in_url))
        context.update({"obj_type": obj_type, "num_results": len(items), "header": f"{PLURAL_NAME} I've created"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class EditAccessSpecializationsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Specialization
    template_name = ITEM_LIST_TEMPLATE_NAME
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        created = list(Specialization.objects.filter(creator=user_in_url))
        items = list(user_in_url.specialization_allowed_editors.all()) + created
        return items

    def get_context_data(self, **kwargs):
        context = super(EditAccessSpecializationsListView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        created = list(Specialization.objects.filter(creator=user_in_url))
        items = list(user_in_url.specialization_allowed_editors.all()) + created
        context.update({"obj_type": obj_type, "num_results": len(set(items)), "header": f"{PLURAL_NAME.capitalize()} I can edit"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class SpecializationDetailView(UserPassesTestMixin, DetailView):
    model = Specialization

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        obj_type = SINGULAR_NAME.lower()
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

        if specialization.group:
            group_profile = get_object_or_404(GroupProfile, group=specialization.group)
        else:
            group_profile = None

        recs = generate_recommendations_from_queryset(queryset=Specialization.objects.all(), obj=specialization)
        print(recs)

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

            "group_profile": group_profile,

            "category": category, 
            "field": field, 
            "courses": courses,

            "recs": recs

        }
        return render(request, 'market/SPECIALIZATION_DESIGN.html', context)


class SpecializationCreateView(LoginRequiredMixin, CreateView):
    model = Specialization
    fields = SPECIALIZATION_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # If user has chosen a group, make sure the user is a member of that group:
        return super().form_valid(form) if formValid(user=form.instance.creator, group=form.instance.group) else super().form_invalid(form)


    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(SpecializationCreateView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        context.update({"obj_type": obj_type, "header": f"Create {SINGULAR_NAME.lower()}"})
        return context


class SpecializationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Specialization
    fields = SPECIALIZATION_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # If user has chosen a group, make sure the user is a member of that group:
        return super().form_valid(form) if formValid(user=form.instance.creator, group=form.instance.group) else super().form_invalid(form)

    def test_func(self):
        # Check if user enrolled in the course.
        specialization = Specialization.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == specialization.creator or self.request.user in specialization.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(SpecializationUpdateView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        context.update({"obj_type": obj_type, "header": f"Update {SINGULAR_NAME.lower()}"})
        return context


class SpecializationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Specialization
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        # Check if user enrolled in the course.
        specialization = Specialization.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == specialization.creator

    def get_context_data(self, **kwargs):
        context = super(SpecializationDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": SINGULAR_NAME.lower()})
        return context



