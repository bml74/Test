from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
from .models import Ecole, Specialization, Course
from django.contrib.auth.decorators import login_required
from .utils import get_obj_by_type_and_id


@login_required
def enroll(request, id, obj_type):
    obj = get_obj_by_type_and_id(obj_type, id)
    if obj.students.filter(id=request.user.id).exists():
        obj.students.remove(request.user)
    else:
        if obj_type == 'specialization':
            # If user enrolls in specialization then user enrolled in all courses
            if isinstance(obj, Specialization): # Affirm that obj is of type Specialization
                courses_within_specialization = Course.objects.filter(specialization=obj) # Get all courses within specialization
                for course in courses_within_specialization: # For each of these courses within the specialization
                    if not course.students.filter(id=request.user.id).exists(): # If user not already enrolled in that course
                        course.students.add(request.user) # Then add user as a student
        obj.students.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
def enroll_in_ecole(request, id):
    ecole = get_object_or_404(Ecole, id=id)
    if ecole.students.filter(id=request.user.id).exists():
        # User has already bookmarked article. The following line removes the bookmark.
        ecole.students.remove(request.user)
    else: # User adding bookmark.
        ecole.students.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def ecoles_home(request):
    return render(request, 'ecoles/ecoles.html', {'title': 'Les Écoles', 'ecoles': Ecole.objects.all()})


def course_info_design(request):
    return render(request, 'market/COURSE_INFO_DESIGN.html')


def course_design(request):
    return render(request, 'market/COURSE_DESIGN.html')


