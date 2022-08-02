from django.contrib import admin
from .models import TwoSidedFinancialTransaction, Entity, Chain, Era, Theme


admin.site.register(TwoSidedFinancialTransaction)
admin.site.register(Entity)
admin.site.register(Chain)
admin.site.register(Era)
admin.site.register(Theme)
