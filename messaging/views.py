from django.shortcuts import render, redirect
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User


from django.core.paginator import Paginator


def inbox(request):
	context = {}
	return render(request, "messaging/inbox.html", context=context)