from django.contrib import admin

from .models import RFIDCard, RFIDLog


class RFIDCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'rfid_hash', 'revoked')


class RFIDLogAdmin(admin.ModelAdmin):
    list_display = ('card', 'time')


admin.site.register(RFIDCard, RFIDCardAdmin)
admin.site.register(RFIDLog, RFIDLogAdmin)
