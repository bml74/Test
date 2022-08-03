from django.shortcuts import render
from .models import Ecole

# import math
# import calendar
# import datetime
# import json
# import requests
# import wikipedia
# from calendar import HTMLCalendar
# from datetime import datetime

# from googletrans import Translator

# from pytube import Playlist, YouTube, extract
# from youtube_transcript_api import YouTubeTranscriptApi
# from strfseconds import strfseconds
# from bs4 import BeautifulSoup as bs

# from django.http import JsonResponse
# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
# from django.contrib.auth.models import User, Group
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import *
# from django.views.generic import (
#     View,
#     ListView,
#     DetailView,
#     CreateView,
#     UpdateView,
#     DeleteView,
# )
# from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# from users.models import Profile
# from news.models import SearchAccessRequest
# from .models import (
#     Exercise, 
#     Food, 
#     CalendarDayNote, 
#     Objective, 
#     Reminder, 
#     Entry, 
#     Operation, 
#     Category, 
#     Field, 
#     Specialization,
#     Course,
#     Module, 
#     Submodule, 
#     Assignment,
#     Task,
#     CorsicanBibleChapter,
#     Transaction
# )
# from .utils import get_obj_by_type_and_id


def ecoles_home(request):


    from parrot import Parrot
    # import torch
    import warnings
    warnings.filterwarnings("ignore")

    ''' 
    uncomment to get reproducable paraphrase generations
    def random_state(seed):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    random_state(1234)
    '''

    #Init models (make sure you init ONLY once if you integrate this to your code)
    parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5")

    phrases = ["Can you recommend some upscale restaurants in Newyork?",
            "What are the famous places we should not miss in Russia?"
    ]

    for phrase in phrases:
        print("-"*100)
        print("Input_phrase: ", phrase)
        print("-"*100)
        para_phrases = parrot.augment(input_phrase=phrase, use_gpu=False)
        for para_phrase in para_phrases:
            print(para_phrase)


    return render(request, 'ecoles/ecoles.html', {'title': 'Les Écoles', 'ecoles': Ecole.objects.all()})


def course_info_design(request):
    return render(request, 'designs/course_info_design.html', {'title': 'Les Écoles'})


def course_design(request):
    return render(request, 'designs/course_design.html', {'title': 'Les Écoles'})

