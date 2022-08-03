from django.contrib import admin

from .models import RFIDCard


class RFIDCardAdmin(admin.ModelAdmin):
    list_display = ("user", "rfid_hash", "revoked")


admin.site.register(RFIDCard, RFIDCardAdmin)
