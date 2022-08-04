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

class CourseListView(UserPassesTestMixin, ListView):
    model = Course
    template_name = 'ecoles/specialization_and_course_list_view.html'
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        obj_type = "course"
        context.update({"obj_type": obj_type, "header": f"{obj_type.capitalize()}s", "title": f"{obj_type.capitalize()}s"})
        return context

    def get_queryset(self):
        return Course.objects.order_by('-title')


class EnrolledCoursesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = 'ecoles/specialization_and_course_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Course.objects.filter(students=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(EnrolledCoursesListView, self).get_context_data(**kwargs)
        obj_type = "course"
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


class CreatedCoursesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = 'ecoles/specialization_and_course_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Course.objects.filter(creator=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(CreatedCoursesListView, self).get_context_data(**kwargs)
        obj_type = "specialization"
        context.update({"obj_type": obj_type, "header": f"{obj_type.capitalize()}s I've created", "title": f"My Creations | {obj_type.capitalize()}"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class EditAccessCoursesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = 'ecoles/specialization_and_course_list_view.html'
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        created = list(Course.objects.filter(creator=user_in_url))
        items = list(user_in_url.course_allowed_editors.all()) + created
        return items

    def get_context_data(self, **kwargs):
        context = super(EditAccessCoursesListView, self).get_context_data(**kwargs)
        obj_type = "specialization"
        context.update({"obj_type": obj_type, "header": f"{obj_type.capitalize()}s I can edit", "title": f"Edit Access | {obj_type.capitalize()}"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class CourseDetailView(UserPassesTestMixin, DetailView):
    model = Course # Commit...

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        obj_type = "course"
        course = get_object_or_404(Course, pk=kwargs['pk'])
        user_enrolled = request.user in course.students.all() 
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
            modules = Module.objects.filter(course=course)
        except AttributeError:
            modules = None

        user_is_creator = request.user == course.creator
        request_already_sent = request.user in course.edit_access_request.all()
        users_with_requests = course.edit_access_request.all()
        users_with_edit_access = course.allowed_editors.all()

        # # Progress bar:
        # total_assignments = 0 # submodules = Submodule.objects.filter(module=module)
        # total_assignments_completed = 0
        # # total_time_to_complete_submodule_in_hours = 0

        # all_modules = {}

        # for module in modules:
        #     submodules = Submodule.objects.filter(module=module)
        #     submodules_within_modules = {}
        #     for submodule in submodules:
        #         total_time_to_complete_submodule_in_hours = 0
        #         assignments = Assignment.objects.filter(submodule=submodule)
        #         num_assignments = len(list(Assignment.objects.filter(submodule=submodule)))
        #         total_assignments += num_assignments
        #         num_assignments_completed = 0
        #         assignments_within_submodules = []
        #         for assignment in assignments:
        #             if request.user in assignment.completed.all():
        #                 num_assignments_completed += 1
        #                 total_assignments_completed += num_assignments_completed
        #                 assignment_data = {"assignment": assignment, "completed": "True"}
        #             else:
        #                 assignment_data = {"assignment": assignment, "completed": "False"}
        #             assignments_within_submodules.append(assignment_data)
        #             total_time_to_complete_submodule_in_hours += assignment.estimated_minutes_to_complete / 60

        #         # submodules_within_modules[submodule] = assignments_within_submodules
        #         submodules_within_modules[submodule] = {"assignments": assignments_within_submodules, "time": math.ceil(total_time_to_complete_submodule_in_hours)}
        #     all_modules[module] = submodules_within_modules            
                
        # try:
        #     pct_completed = int((total_assignments_completed / (total_assignments)) * 100)
        # except ZeroDivisionError:
        #     pct_completed = 0

        context = {
            "obj_type": obj_type, 
            "item": course, 
            "course": course, 
            "user_enrolled": user_enrolled,
            "allowed_to_edit": allowed_to_edit,
            "user_is_creator": user_is_creator,
            "request_already_sent": request_already_sent,
            "users_with_requests": users_with_requests,
            "users_with_edit_access": users_with_edit_access,
            # "pct_completed": pct_completed,

            "category": category, 
            "field": field, 
            "specialization": specialization, 
            "modules": modules,

            # "all_modules": all_modules,

        }
        return render(request, 'ecoles/courses/course_detail_view.html', context)


class CourseInfoDetailView(UserPassesTestMixin, DetailView):
    model = Course

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        obj_type = "course"
        course = get_object_or_404(Course, pk=kwargs['pk'])
        user_enrolled = request.user in course.students.all() 
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
            modules = Module.objects.filter(course=course)
        except AttributeError:
            modules = None

        # followers_of_user = FollowersCount.objects.filter(user_being_followed=course.creator)
        # num_followers_of_creator = len(followers_of_user)

        user_is_creator = request.user == course.creator # Did user logged in create course?

        # logged_in_user_follows_course_creator = False # If logged in user isn't creator ... Do they follow the course creator or not>
        # if not user_is_creator: # If user isn't creator
        #     if course.creator is not request.user: # Does user logged in follow course creator ... if user logged in is not course creator???
        #         followers_of_course_creator = FollowersCount.objects.filter(user_being_followed=course.creator) # Get all followers of course creator
        #         followers_of_course_creator = [f.follower_of_user for f in followers_of_course_creator] # All user objects following course creator
        #         if request.user in followers_of_course_creator:
        #             logged_in_user_follows_course_creator = True
        
        # request_already_sent = request.user in course.edit_access_request.all()
        # users_with_requests = course.edit_access_request.all()
        # users_with_edit_access = course.allowed_editors.all()


        # # All assignments in this course (https://stackoverflow.com/questions/9099544/filtering-through-two-foreign-key-relationships-in-django/9099736):
        # assignments = Assignment.objects.filter(submodule__module__course__title="False Flag Operations")
        # assignment_times = [a.estimated_minutes_to_complete for a in assignments]
        # estimated_total_course_time = math.ceil(sum(assignment_times) / 60)
        # print(estimated_total_course_time)

        context = {
            "obj_type": obj_type, 
            "item": course, 
            "course": course, 
            # "estimated_total_course_time": estimated_total_course_time,
            "user_enrolled": user_enrolled,
            "allowed_to_edit": allowed_to_edit,
            "user_is_creator": user_is_creator,
            # "request_already_sent": request_already_sent,
            # "users_with_requests": users_with_requests,
            # "users_with_edit_access": users_with_edit_access,

            "category": category, 
            "field": field, 
            "specialization": specialization, 
            "modules": modules,

            # "num_followers_of_creator": num_followers_of_creator,

            # "logged_in_user_follows_course_creator": logged_in_user_follows_course_creator

        }
        return render(request, 'ecoles/courses/course_info_detail_view.html', context)


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    fields = ['title', 'field', 'visibility', 'difficulty_level', 'description', 'specialization', 'creator']
    template_name = 'ecoles/ecoles_form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(CourseCreateView, self).get_context_data(**kwargs)
        obj_type = "course"
        context.update({"obj_type": obj_type, "header": f"Create {obj_type}"})
        return context


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    fields = ['title', 'field', 'visibility', 'difficulty_level', 'description', 'specialization', 'creator']
    template_name = 'ecoles/ecoles_form_view.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        # Check if user created the course.
        course = Course.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == course.creator

    def get_context_data(self, **kwargs):
        context = super(CourseUpdateView, self).get_context_data(**kwargs)
        obj_type = "course"
        context.update({"obj_type": obj_type, "header": f"Create {obj_type}"})
        return context


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = 'ecoles/confirm_delete_view.html'

    def test_func(self):
        course = Course.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == course.creator

    def get_context_data(self, **kwargs):
        context = super(CourseDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": "course"})
        return context

