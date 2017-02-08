from django.contrib import admin

from .models import RFIDCard, RFIDLog


admin.site.register(RFIDCard)
admin.site.register(RFIDLog)
