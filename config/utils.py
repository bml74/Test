import sys
import csv
import pandas as pd
from googletrans import Translator
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from orgs.models import GroupProfile


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