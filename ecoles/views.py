from django.shortcuts import render
from .models import Ecole


def ecoles_home(request):
    return render(request, 'ecoles/ecoles.html', {'title': 'Les Écoles', 'ecoles': Ecole.objects.all()})

