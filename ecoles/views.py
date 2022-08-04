from django.shortcuts import render, HttpResponseRedirect
from .models import Ecole
from django.contrib.auth.decorators import login_required
from .utils import get_obj_by_type_and_id


@login_required
def enroll(request, id, obj_type):
    obj = get_obj_by_type_and_id(obj_type, id)
    if obj.students.filter(id=request.user.id).exists():
        # User has already bookmarked article. The following line removes the bookmark.
        obj.students.remove(request.user)
    else: # User adding bookmark.
        obj.students.add(request.user)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def ecoles_home(request):
    return render(request, 'ecoles/ecoles.html', {'title': 'Les Écoles', 'ecoles': Ecole.objects.all()})


def course_info_design(request):
    return render(request, 'designs/course_info_design.html', {'title': 'Les Écoles'})


def course_design(request):
    return render(request, 'designs/course_design.html', {'title': 'Les Écoles'})


