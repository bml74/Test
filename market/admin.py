from django.contrib import admin
from .models import Listing, Fundraiser, Transaction, SuggestedDelivery


admin.site.register(Listing)
admin.site.register(Fundraiser)
admin.site.register(Transaction)
admin.site.register(SuggestedDelivery)
