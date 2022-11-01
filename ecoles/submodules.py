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
    Course,
    Module, 
    Submodule, 
    Assignment,
)
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME
from config.abstract_settings.model_fields import SUBMODULE_FIELDS


SINGULAR_NAME = "Submodule"
PLURAL_NAME = "Submodules"


class SubmoduleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Submodule
    template_name = 'ecoles/submodules/submodule_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        module = get_object_or_404(Module, id=self.kwargs.get('module_id'))
        items = list(Submodule.objects.filter(module=module))
        return items

    def get_context_data(self, **kwargs):
        context = super(SubmoduleListView, self).get_context_data(**kwargs)
        module = get_object_or_404(Module, id=self.kwargs.get('module_id'))
        course = module.course
        title = f"{PLURAL_NAME} | " + module.title + " | " + course.title
        context.update({"obj_type": SINGULAR_NAME.lower(), "title": title, "header": title, "course": course, "module": module})
        return context

    def test_func(self):
        # Check if user enrolled in the course.
        module = Module.objects.filter(id=self.kwargs['module_id'])[0]
        course = module.course
        return self.request.user in course.students.all() or self.request.user == course.creator or self.request.user in course.allowed_editors.all()


class SubmoduleDetailView(UserPassesTestMixin, DetailView):
    model = Submodule

    def test_func(self):
        # Check if user enrolled in the course.
        submodule = Submodule.objects.filter(id=self.kwargs['pk'])[0]
        module = submodule.module
        course = module.course
        return self.request.user in course.students.all() or self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get(self, request, *args, **kwargs):
        submodule = get_object_or_404(Submodule, pk=kwargs['pk'])
        module = get_object_or_404(Module, pk=submodule.module.id)
        course = get_object_or_404(Course, pk=module.course.id)
        allowed_to_edit = request.user in course.allowed_editors.all()
        specialization = course.specialization
        field = get_object_or_404(Field, pk=course.field.id)
        category = get_object_or_404(Category, pk=field.category.id)
        assignments = Assignment.objects.filter(submodule=submodule)

        # arr_of_arrs = generate_keywords(submodule)

        # # Progress bar:
        # total = 0
        # num_total_assignments = len(list(assignments)) # assignments = Assignment.objects.filter(submodule=submodule)
        # for assignment in assignments: 
        #     assignment_completed = request.user in assignment.completed.all()
        #     if assignment_completed:
        #         total += 1
        # try:
        #     pct_completed = int((total / (num_total_assignments)) * 100)
        # except ZeroDivisionError:
        #     pct_completed = 0

        context = {
            "obj_type": SINGULAR_NAME.lower(), 
            "item": submodule, 
            "submodule": submodule,
            "allowed_to_edit": allowed_to_edit,
            # "pct_completed": pct_completed,

            "category": category, 
            "field": field, 
            "specialization": specialization, 
            "course": course, 
            "module": module,
            "assignments": assignments,

        }
        return render(request, 'ecoles/submodules/submodule_detail_view.html', context)


class SubmoduleCreateView(LoginRequiredMixin, CreateView):
    model = Submodule
    fields = SUBMODULE_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user is creator or an allowed editor.
        module = Module.objects.filter(id=self.kwargs['module_id'])[0]
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(SubmoduleCreateView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        context.update({"obj_type": obj_type, "header": f"Create {SINGULAR_NAME.lower()}"})
        return context


class SubmoduleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Submodule
    fields = SUBMODULE_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user is creator or an allowed editor.
        module = Module.objects.filter(id=self.kwargs['module_id'])[0]
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(SubmoduleUpdateView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        context.update({"obj_type": obj_type, "header": f"Update {SINGULAR_NAME.lower()}"})
        return context


class SubmoduleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Submodule
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        # Check if user is creator or an allowed editor.
        module = Module.objects.filter(id=self.kwargs['module_id'])[0]
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(SubmoduleDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": SINGULAR_NAME.lower()})
        return context


