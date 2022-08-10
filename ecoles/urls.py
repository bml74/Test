from django.contrib import admin
from django.urls import path
from . import views, categories, fields, specializations, courses, modules, submodules, assignments, tasks


urlpatterns = [

    path('', views.ecoles_home, name='ecoles-home'),

    path('enroll/<str:obj_type>/<int:id>/', views.enroll, name='enroll'),

    path('enroll/<int:id>/', views.enroll_in_ecole, name='enroll_in_ecole'),

    path('courseinfo/', views.course_info_design, name='course-info-design'),
    path('course/', views.course_design, name='course-design'),

    path('categories/', categories.CategoryListView.as_view(), name='categories'),
    path('categories/list/', categories.CategoryListView.as_view(), name='categories_list'),
    path('categories/enrolled/<str:username>/', categories.EnrolledCategoriesListView.as_view(), name='categories_enrolled'),
    path('categories/created/<str:username>/', categories.CreatedCategoriesListView.as_view(), name='categories_created'),
    path('categories/editaccess/<str:username>/', categories.EditAccessCategoriesListView.as_view(), name='categories_edit_access'),
    path('categories/new/', categories.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/', categories.CategoryDetailView.as_view(), name='category_detail'),
    path('categories/update/<int:pk>/', categories.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/delete/<int:pk>/', categories.CategoryDeleteView.as_view(), name='category_delete'),

    path('fields/', fields.FieldListView.as_view(), name='fields'),
    path('fields/list/', fields.FieldListView.as_view(), name='fields_list'),
    path('fields/enrolled/<str:username>/', fields.EnrolledFieldsListView.as_view(), name='fields_enrolled'),
    path('fields/created/<str:username>/', fields.CreatedFieldsListView.as_view(), name='fields_created'),
    path('fields/editaccess/<str:username>/', fields.EditAccessFieldsListView.as_view(), name='fields_edit_access'),
    path('fields/new/', fields.FieldCreateView.as_view(), name='field_create'),
    path('fields/<int:pk>/', fields.FieldDetailView.as_view(), name='field_detail'),
    path('fields/update/<int:pk>/', fields.FieldUpdateView.as_view(), name='field_update'),
    path('fields/delete/<int:pk>/', fields.FieldDeleteView.as_view(), name='field_delete'),

    path('specializations/', specializations.SpecializationListView.as_view(), name='specializations'),
    path('specializations/list/', specializations.SpecializationListView.as_view(), name='specializations_list'),
    path('specializations/enrolled/<str:username>/', specializations.EnrolledSpecializationsListView.as_view(), name='specializations_enrolled'),
    path('specializations/created/<str:username>/', specializations.CreatedSpecializationsListView.as_view(), name='specializations_created'),
    path('specializations/editaccess/<str:username>/', specializations.EditAccessSpecializationsListView.as_view(), name='specializations_edit_access'),
    path('specializations/new/', specializations.SpecializationCreateView.as_view(), name='specialization_create'),
    path('specializations/<int:pk>/', specializations.SpecializationDetailView.as_view(), name='specialization_detail'),
    path('specializations/update/<int:pk>/', specializations.SpecializationUpdateView.as_view(), name='specialization_update'),
    path('specializations/delete/<int:pk>/', specializations.SpecializationDeleteView.as_view(), name='specialization_delete'),

    
    path('courses/', courses.CourseListView.as_view(), name='courses'),
    path('courses/list/', courses.CourseListView.as_view(), name='courses_list'),
    path('courses/enrolled/<str:username>/', courses.EnrolledCoursesListView.as_view(), name='courses_enrolled'),
    path('courses/created/<str:username>/', courses.CreatedCoursesListView.as_view(), name='courses_created'),
    path('courses/editaccess/<str:username>/', courses.EditAccessCoursesListView.as_view(), name='courses_edit_access'),
    path('courses/new/', courses.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/', courses.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:pk>/info/', courses.CourseInfoDetailView.as_view(), name='course_info_detail'),
    path('courses/update/<int:pk>/', courses.CourseUpdateView.as_view(), name='course_update'),
    path('courses/delete/<int:pk>/', courses.CourseDeleteView.as_view(), name='course_delete'),

    path('course/<int:course_id>/modules/', modules.ModuleListView.as_view(), name='modules'),
    path('course/<int:course_id>/modules/list/', modules.ModuleListView.as_view(), name='modules_list'),
    path('course/<int:course_id>/modules/new/', modules.ModuleCreateView.as_view(), name='module_create'),
    path('course/<int:course_id>/modules/<int:pk>/', modules.ModuleDetailView.as_view(), name='module_detail'),
    path('course/<int:course_id>/modules/update/<int:pk>/', modules.ModuleUpdateView.as_view(), name='module_update'),
    path('course/<int:course_id>/modules/delete/<int:pk>/', modules.ModuleDeleteView.as_view(), name='module_delete'),

    path('course/<int:course_id>/module/<int:module_id>/submodules/', submodules.SubmoduleListView.as_view(), name='submodules'),
    path('course/<int:course_id>/module/<int:module_id>/submodules/list/', submodules.SubmoduleListView.as_view(), name='submodules_list'),
    path('course/<int:course_id>/module/<int:module_id>/submodules/new/', submodules.SubmoduleCreateView.as_view(), name='submodule_create'),
    path('course/<int:course_id>/module/<int:module_id>/submodules/<int:pk>/', submodules.SubmoduleDetailView.as_view(), name='submodule_detail'),
    path('course/<int:course_id>/module/<int:module_id>/submodules/update/<int:pk>/', submodules.SubmoduleUpdateView.as_view(), name='submodule_update'),
    path('course/<int:course_id>/module/<int:module_id>/submodules/delete/<int:pk>/', submodules.SubmoduleDeleteView.as_view(), name='submodule_delete'),

    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignments/', assignments.AssignmentListView.as_view(), name='assignments'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignments/list/', assignments.AssignmentListView.as_view(), name='assignments_list'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignments/new/', assignments.AssignmentCreateView.as_view(), name='assignment_create'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignments/<int:pk>/', assignments.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignments/update/<int:pk>/', assignments.AssignmentUpdateView.as_view(), name='assignment_update'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignments/delete/<int:pk>/', assignments.AssignmentDeleteView.as_view(), name='assignment_delete'),

    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignment/<int:assignment_id>/tasks/', tasks.TaskListView.as_view(), name='tasks'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignment/<int:assignment_id>/tasks/list/', tasks.TaskListView.as_view(), name='tasks_list'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignment/<int:assignment_id>/tasks/new/', tasks.TaskCreateView.as_view(), name='task_create'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignment/<int:assignment_id>/tasks/<int:pk>/<str:username>/', tasks.TaskDetailView.as_view(), name='task_detail'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignment/<int:assignment_id>/tasks/update/<int:pk>/<str:username>/', tasks.TaskUpdateView.as_view(), name='task_update'),
    path('course/<int:course_id>/module/<int:module_id>/submodule/<int:submodule_id>/assignment/<int:assignment_id>/tasks/delete/<int:pk>/<str:username>/', tasks.TaskDeleteView.as_view(), name='task_delete'),

]
