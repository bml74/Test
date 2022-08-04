from django.shortcuts import render
from .models import Ecole

def ecoles_home(request):
    return render(request, 'ecoles/ecoles.html', {'title': 'Les Écoles', 'ecoles': Ecole.objects.all()})


def course_info_design(request):
    return render(request, 'designs/course_info_design.html', {'title': 'Les Écoles'})


def course_design(request):
    return render(request, 'designs/course_design.html', {'title': 'Les Écoles'})


