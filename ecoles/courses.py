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
    Course,
    Module, 
    Submodule, 
    Assignment
)
import math
from .datatools import generate_recommendations_from_queryset
from config.abstract_settings.model_fields import COURSE_FIELDS
from config.abstract_settings.template_names import FORM_VIEW_TEMPLATE_NAME, CONFIRM_DELETE_TEMPLATE_NAME, ITEM_LIST_TEMPLATE_NAME
from config.utils import formValid


SINGULAR_NAME = "Course"
PLURAL_NAME = "Courses"


class CourseListView(UserPassesTestMixin, ListView):
    model = Course
    template_name = ITEM_LIST_TEMPLATE_NAME # ecoles/specialization_and_course_list_view.html
    context_object_name = 'items'

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(CourseListView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        context.update({"obj_type": obj_type, "num_results": len(Course.objects.all()), "header": PLURAL_NAME})
        return context

    def get_queryset(self):
        return Course.objects.order_by('-title')


class EnrolledCoursesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = ITEM_LIST_TEMPLATE_NAME
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Course.objects.filter(students=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(EnrolledCoursesListView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Course.objects.filter(students=user_in_url))
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


class CreatedCoursesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = ITEM_LIST_TEMPLATE_NAME
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Course.objects.filter(creator=user_in_url))
        return items

    def get_context_data(self, **kwargs):
        context = super(CreatedCoursesListView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        items = list(Course.objects.filter(creator=user_in_url))
        context.update({"obj_type": obj_type, "num_results": len(items), "header": f"{PLURAL_NAME} I've created"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


class EditAccessCoursesListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Course
    template_name = ITEM_LIST_TEMPLATE_NAME
    context_object_name = 'items'

    def get_queryset(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        created = list(Course.objects.filter(creator=user_in_url))
        items = list(user_in_url.course_allowed_editors.all()) + created
        return items

    def get_context_data(self, **kwargs):
        context = super(EditAccessCoursesListView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        created = list(Course.objects.filter(creator=user_in_url))
        items = list(user_in_url.course_allowed_editors.all()) + created
        context.update({"obj_type": obj_type, "num_results": len(set(items)), "header": f"{PLURAL_NAME} I can edit"})
        return context

    def test_func(self):
        user_in_url = get_object_or_404(User, username=self.kwargs.get('username'))
        return user_in_url == self.request.user


def get_details(request, modules):
    # Progress bar:
    total_assignments = 0 # submodules = Submodule.objects.filter(module=module)
    total_assignments_completed = 0
    # total_time_to_complete_submodule_in_hours = 0
    all_modules = {}
    for module in modules:
        submodules = Submodule.objects.filter(module=module)
        submodules_within_modules = {}
        for submodule in submodules:
            total_time_to_complete_submodule_in_hours = 0
            assignments = Assignment.objects.filter(submodule=submodule)
            num_assignments = len(list(Assignment.objects.filter(submodule=submodule)))
            total_assignments += num_assignments
            num_assignments_completed = 0
            assignments_within_submodules = []
            for assignment in assignments:
                if request.user in assignment.completed.all():
                    num_assignments_completed += 1
                    total_assignments_completed += 1
                    assignment_data = {"assignment": assignment, "completed": "True"}
                else:
                    assignment_data = {"assignment": assignment, "completed": "False"}
                assignments_within_submodules.append(assignment_data)
                total_time_to_complete_submodule_in_hours += assignment.estimated_minutes_to_complete / 60

            # submodules_within_modules[submodule] = assignments_within_submodules
            submodules_within_modules[submodule] = {"assignments": assignments_within_submodules, "time": math.ceil(total_time_to_complete_submodule_in_hours)}
        all_modules[module] = submodules_within_modules            
            
    try:
        pct_completed = int((total_assignments_completed / (total_assignments)) * 100)
    except ZeroDivisionError:
        pct_completed = 0
    
    return (all_modules, pct_completed)

      
class CourseDetailView(UserPassesTestMixin, DetailView):
    model = Course # Commit...

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        obj_type = SINGULAR_NAME.lower()
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

        if course.group:
            group_profile = get_object_or_404(GroupProfile, group=course.group)
        else:
            group_profile = None

        # Create Pandas dataframe for content-based recommendation system. For now, only title and description are needed.
        # df = get_df(Course) # Create Pandas DF of all the instances of the obj but put only the columns title and category
        # (title, cosine_sim, indices) = prep_for_recs(df, course)
        # recs = get_recs(df, title, cosine_sim, indices)
        # print(recs)
        recs = generate_recommendations_from_queryset(queryset=Course.objects.all(), obj=course)
        print(recs)
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
        (all_modules, pct_completed) = get_details(request, modules)

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
            "pct_completed": pct_completed,

            "group_profile": group_profile,

            "category": category, 
            "field": field, 
            "specialization": specialization, 
            "modules": modules,

            "all_modules": all_modules,

            "recs": recs

        }
        return render(request, 'market/COURSE_DESIGN.html', context)


class CourseInfoDetailView(UserPassesTestMixin, DetailView):
    model = Course

    def test_func(self):
        return self.request.user.is_authenticated

    def get(self, request, *args, **kwargs):
        obj_type = SINGULAR_NAME.lower()
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


        # All assignments in this course (https://stackoverflow.com/questions/9099544/filtering-through-two-foreign-key-relationships-in-django/9099736):
        assignments = Assignment.objects.filter(submodule__module__course__title=course.title)
        assignment_times = [a.estimated_minutes_to_complete for a in assignments]
        estimated_total_course_time = math.ceil(sum(assignment_times) / 60)
        print(f"Estimated total course time: {estimated_total_course_time}")

        (all_modules, pct_completed) = get_details(request, modules)

        context = {
            "obj_type": obj_type, 
            "item": course, 
            "course": course, 
            "estimated_total_course_time": estimated_total_course_time,
            "user_enrolled": user_enrolled,
            "allowed_to_edit": allowed_to_edit,
            "user_is_creator": user_is_creator,
            # "request_already_sent": request_already_sent,
            # "users_with_requests": users_with_requests,
            # "users_with_edit_access": users_with_edit_access,

            "pct_completed": pct_completed,
            "all_modules": all_modules,

            "category": category, 
            "field": field, 
            "specialization": specialization, 
            "modules": modules,

            # "num_followers_of_creator": num_followers_of_creator,

            # "logged_in_user_follows_course_creator": logged_in_user_follows_course_creator

        }
        return render(request, 'market/COURSE_INFO_DESIGN.html', context)


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    fields = COURSE_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # If user has chosen a group, make sure the user is a member of that group:
        return super().form_valid(form) if formValid(user=form.instance.creator, group=form.instance.group) else super().form_invalid(form)

    def test_func(self):
        return self.request.user.is_authenticated

    def get_context_data(self, **kwargs):
        context = super(CourseCreateView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        context.update({"obj_type": obj_type, "header": f"Create {SINGULAR_NAME.lower()}"})
        return context


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    fields = COURSE_FIELDS
    template_name = FORM_VIEW_TEMPLATE_NAME

    def form_valid(self, form):
        form.instance.creator = self.request.user
        # If user has chosen a group, make sure the user is a member of that group:
        return super().form_valid(form) if formValid(user=form.instance.creator, group=form.instance.group) else super().form_invalid(form)

    def test_func(self):
        # Check if user created the course.
        course = Course.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == course.creator or self.request.user in course.allowed_editors.all()

    def get_context_data(self, **kwargs):
        context = super(CourseUpdateView, self).get_context_data(**kwargs)
        obj_type = SINGULAR_NAME.lower()
        context.update({"obj_type": obj_type, "header": f"Update {SINGULAR_NAME.lower()}"})
        return context


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    success_url = '/ecoles/'
    context_object_name = 'item'
    template_name = CONFIRM_DELETE_TEMPLATE_NAME

    def test_func(self):
        course = Course.objects.filter(id=self.kwargs['pk'])[0]
        return self.request.user == course.creator

    def get_context_data(self, **kwargs):
        context = super(CourseDeleteView, self).get_context_data(**kwargs)
        context.update({"obj_type": SINGULAR_NAME.lower()})
        return context


