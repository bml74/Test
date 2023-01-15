from django.contrib import admin
from .models import (
    Listing, 
    Fundraiser, 
    Transaction, 
    SuggestedDelivery, 
    PaymentIntentTracker,
    Lottery,
    LotteryParticipant
)


admin.site.register(Listing)
admin.site.register(Fundraiser)
admin.site.register(Transaction)
admin.site.register(SuggestedDelivery)
admin.site.register(PaymentIntentTracker)
admin.site.register(Lottery)
admin.site.register(LotteryParticipant)
