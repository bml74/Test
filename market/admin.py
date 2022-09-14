from django.contrib import admin
from .models import Listing, Fundraiser, Transaction


admin.site.register(Listing)
admin.site.register(Fundraiser)
admin.site.register(Transaction)
