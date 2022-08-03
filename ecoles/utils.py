from .models import Category, Field, Specialization, Course
from django.shortcuts import get_object_or_404


def get_obj_by_type_and_id(obj_type, obj_id):
    obj_types = {obj.__name__.lower(): obj for obj in [Category, Field, Specialization, Course]}
    item = get_object_or_404(obj_types[obj_type], id=obj_id)
    return item