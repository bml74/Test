from django.shortcuts import get_object_or_404, render, HttpResponseRedirect
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


