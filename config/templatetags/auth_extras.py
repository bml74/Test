from django import template
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name): 
    group = Group.objects.get(name=group_name) 
    return True if group in user.groups.all() else False


@register.filter
def get_username_from_id(id):
    return get_object_or_404(User, id=id).username

