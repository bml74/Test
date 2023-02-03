import sys
import csv
import pandas as pd
from googletrans import Translator
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from orgs.models import GroupProfile
from django.contrib.auth.models import Group
from users.models import Rating


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def translate_phrase(src="en", dest="en", phrase=""):
    translator = Translator()
    res = translator.translate(phrase, src=src, dest=dest)
    return {"src": res.src, "dest": res.dest, "translated_text": res.text, "original_text": phrase}


def download_file(request, queryset, CONTENT_TYPE, FILE_TYPE, FILE_EXTENSION):
    if not request.user.is_staff:
        raise PermissionDenied

    model = queryset.model
    model_fields = model._meta.fields + model._meta.many_to_many
    field_names = [field.name for field in model_fields]

    response = HttpResponse(content_type=f'{CONTENT_TYPE}/{FILE_EXTENSION}')
    response['Content-Disposition'] = 'attachment; filename="export.{FILE_EXTENSION}"'

    # the csv writer
    writer = csv.writer(response, delimiter=",")
    # Write a first row with header information
    writer.writerow(field_names)
    # Write data rows
    for row in queryset:
        values = []
        for field in field_names:
            value = getattr(row, field)
            if callable(value):
                try:
                    value = value() or ''
                except:
                    value = 'Error retrieving value'
            if value is None:
                value = ''
            values.append(value)
        writer.writerow(values)
    return response


def get_as_df(queryset):

    model = queryset.model
    print(f"MODEL: {model}")
    model_fields = model._meta.fields + model._meta.many_to_many
    field_names = [field.name for field in model_fields]
  
    df = pd.DataFrame(columns=field_names)

    print(queryset)

    # Write data rows
    for row in queryset:
        values = []
        for field in field_names:
            value = getattr(row, field)
            if callable(value):
                try:
                    value = value() or ''
                except:
                    value = 'Error retrieving value'
            if value is None:
                value = ''
            values.append(value)
        df.loc[len(df.index)] = values
    return df


def getGroupProfile(group):
    return get_object_or_404(GroupProfile, group=group)

def userIsPartOfGroup(user, group):
    group_profile = getGroupProfile(group)
    return group_profile.group_members.filter(id=user.id).exists() or user.groups.filter(id=group.id).exists()

def userCreatedGroup(user, group):
    group_profile = getGroupProfile(group)
    return user == group_profile.group_creator

def formValid(user, group):
    # Takes a user and group. If group has been specified, makes sure user
    # is part of group. If so, returns form is valid.
    if group:
        return True if userIsPartOfGroup(user, group) or userCreatedGroup(user, group) else False
    return True
    

"""
# Old:

group = form.instance.group
        if group is None:
            return super().form_valid(form)
        else: # Group is selected 
            group_profile = get_object_or_404(GroupProfile, group=group)
            if form.instance.creator == group_profile.group_creator or group_profile.group_members.filter(id=form.instance.creator.id).exists():
                return super().form_valid(form)
            else:
                return super().form_invalid(form)

"""


def get_group_and_group_profile_from_group_id(group_id):
    # First get the Group in question
    group_obj = Group.objects.filter(id=group_id).first()
    # Then get the group's profile
    group_profile_obj = GroupProfile.objects.filter(group=group_obj).first()
    return (group_obj, group_profile_obj)


def runningDevServer():
    RUNNING_DEVSERVER = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')
    return RUNNING_DEVSERVER


def getDomain():
    if runningDevServer():
        BASE_DOMAIN = 'http://127.0.0.1:8000' 
    else:
        BASE_DOMAIN = 'https://www.hoyabay.com'
    return BASE_DOMAIN


def getOverallRating(user_being_rated):
    overall_ratings = Rating.objects.filter(user_being_rated=user_being_rated).all()
    if overall_ratings:
        overall_rating = 0
        for r in overall_ratings:
            overall_rating += r.rating
        overall_rating /= len(overall_ratings)
        return overall_rating
    return 0


def myround(x, base=10):
    return base * round(x/base)
