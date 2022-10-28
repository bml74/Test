import sys
import csv
from googletrans import Translator
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def translate_phrase(src="en", dest="en", phrase=""):
    translator = Translator()
    res = translator.translate(phrase, src=src, dest=dest)
    return {"src": res.src, "dest": res.dest, "translated_text": res.text, "original_text": phrase}


def download_csv(request, queryset):
    if not request.user.is_staff:
        raise PermissionDenied

    model = queryset.model
    model_fields = model._meta.fields + model._meta.many_to_many
    field_names = [field.name for field in model_fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'

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
