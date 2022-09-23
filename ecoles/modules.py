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
    Assignment
)


class ModuleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Module
    template_name = 'ecoles/modules/module_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        items = list(Module.objects.filter(course=course))
        return items

    def get_context_data(self, **kwargs):
        context = super(ModuleListView, self).get_context_data(**kwargs)
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        title = "Modules | " + course.title
        context.update({"obj_type": "module", "title": title, "header": title, "course": course})
        return context


    def test_func(self):
        # Check if user enrolled in the course.
        course = Course.objects.filter(id=self.kwargs['course_id'])[0]
        return self.request.user in course.students.all() or self.request.user == course.creator or self.request.user in course.allowed_editors.all()


class ModuleDetailView(UserPassesTestMixin, DetailView):
    model = Module

    def test_func(self):
        # Check if user enrolled in the course.
        module = Module.objects.filter(id=self.kwargs['pk'])[0]
        course = module.course
        return self.request.user in course.students.all() or self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get(self, request, *args, **kwargs):
        module = get_object_or_404(Module, pk=kwargs['pk'])
        course = get_object_or_404(Course, pk=module.course.id)
        allowed_to_edit = request.user in course.allowed_editors.all()
        specialization = course.specialization
        try:
            field = get_object_or_404(Field, pk=course.field.id)
        except AttributeError:
            field = None
        try:
            category = get_object_or_404(Category, pk=field.category.id)
        except AttributeError:
            category = None
        try:
            submodules = Submodule.objects.filter(module=module)
        except AttributeError:
            submodules = None

        # Progress bar:
        total_assignments = 0 # submodules = Submodule.objects.filter(module=module)
        total_assignments_completed = 0
        for submodule in submodules:
            assignments = Assignment.objects.filter(submodule=submodule)
            num_assignments = len(list(Assignment.objects.filter(submodule=submodule)))
            total_assignments += num_assignments
            num_assignments_completed = 0
            for assignment in assignments:
                if request.user in assignment.completed.all():
                    num_assignments_completed += 1
                    total_assignments_completed += 1
        try:
            pct_completed = int((total_assignments_completed / (total_assignments)) * 100)
        except ZeroDivisionError:
            pct_completed = 0

        context = {
            "obj_type": "module", 
            "item": module, 
            "module": module, 
            "allowed_to_edit": allowed_to_edit,
            "pct_completed": pct_completed,

            "category": category, 
            "field": field, 
            "specialization": specialization, 
            "course": course, 
            "submodules": submodules,

        }
        return render(request, 'ecoles/modules/module_detail_view.html', context)


class ModuleCreateView(LoginRequiredMixin, CreateView):
    model = Module
    fields = ['title', 'course', 'description'] # , 'visibility'
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user is creator or an allowed editor.
        course = Course.objects.filter(id=self.kwargs['course_id'])[0]
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(ModuleCreateView, self).get_context_data(**kwargs)
        obj_type = "module"
        context.update({"obj_type": obj_type, "header": f"Create {obj_type}"})
        return context


class ModuleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Module
    fields = ['title', 'course', 'description'] # , 'visibility'
    template_name = 'market/dashboard/form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user is creator or an allowed editor.
        course = Course.objects.filter(id=self.kwargs['course_id'])[0]
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(ModuleUpdateView, self).get_context_data(**kwargs)
        obj_type = "module"
        context.update({"obj_type": obj_type, "header": f"Update {obj_type}"})
        return context


class ModuleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Module
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = 'ecoles/confirm_delete_view.html'

    def test_func(self):
        # Check if user is creator or an allowed editor.
        course = Course.objects.filter(id=self.kwargs['course_id'])[0]
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(ModuleDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": "module"})
        return context



