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
    Task,
)
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME
from config.abstract_settings.model_fields import TASK_FIELDS

class TaskListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Task
    template_name = 'ecoles/tasks/task_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        assignment = get_object_or_404(Assignment, id=self.kwargs.get('assignment_id'))
        items = list(Task.objects.filter(assignment=assignment))
        return items

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        assignment = get_object_or_404(Assignment, id=self.kwargs.get('assignment_id'))
        submodule = assignment.submodule
        module = submodule.module
        course = module.course
        title = "Tasks | " + assignment.title + " | " + submodule.title + " | " + module.title + " | " + course.title
        context.update({"obj_type": "task", "title": title, "header": title, "course": course, "module": module, "submodule": submodule, "assignment": assignment})
        return context

    def test_func(self):
        # Check if user enrolled in the course.
        assignment = Assignment.objects.filter(id=self.kwargs['assignment_id'])[0]
        submodule = assignment.submodule
        module = submodule.module
        course = module.course
        return self.request.user in course.students.all() and self.request.user is assignment.creator


class TaskDetailView(UserPassesTestMixin, DetailView):
    model = Task

    def test_func(self):
        # Check if user enrolled in the course.
        task = Task.objects.filter(id=self.kwargs['pk'])[0]
        assignment = Assignment.objects.filter(id=self.kwargs['assignment_id'])[0]
        submodule = assignment.submodule
        module = submodule.module
        course = module.course
        return self.request.user in course.students.all() and self.request.user == task.creator

    def get(self, request, *args, **kwargs):
        task = get_object_or_404(Task, pk=kwargs['pk'])
        assignment = get_object_or_404(Assignment, pk=task.assignment.id)
        submodule = get_object_or_404(Submodule, pk=assignment.submodule.id)
        module = get_object_or_404(Module, pk=submodule.module.id)
        course = get_object_or_404(Course, pk=module.course.id)
        allowed_to_edit = request.user in course.allowed_editors.all()
        specialization = course.specialization
        field = get_object_or_404(Field, pk=course.field.id)
        category = get_object_or_404(Category, pk=field.category.id)
        context = {
            "obj_type": "task",
            "item": task,
            "task": task,
            "allowed_to_edit": allowed_to_edit,

            "category": category, 
            "field": field, 
            "specialization": specialization, 
            "course": course, 
            "module": module,
            "submodule": submodule, 
            "assignment": assignment, 
        }
        return render(request, 'ecoles/tasks/task_detail_view.html', context)


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = TASK_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(TaskCreateView, self).get_context_data(**kwargs)
        obj_type = "task"
        context.update({"obj_type": obj_type, "header": f"Create {obj_type}"})
        return context

    def test_func(self):
        # Check if user is creator or an allowed editor.
        assignment = Assignment.objects.filter(id=self.kwargs['assignment_id'])[0]
        submodule = assignment.submodule
        module = submodule.module
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()


class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    fields = TASK_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user is creator or an allowed editor.
        assignment = Assignment.objects.filter(id=self.kwargs['assignment_id'])[0]
        submodule = assignment.submodule
        module = submodule.module
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        obj_type = "task"
        context.update({"obj_type": obj_type, "header": f"Update {obj_type}"})
        return context


class TaskDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Task
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        # Check if user is creator or an allowed editor.
        assignment = Assignment.objects.filter(id=self.kwargs['assignment_id'])[0]
        submodule = assignment.submodule
        module = submodule.module
        course = module.course
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(TaskDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": "task"})
        return context


