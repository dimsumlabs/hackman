from django.contrib import admin

from . import models


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'valid_until')


class PaymentInvalidAdmin(admin.ModelAdmin):
    list_display = ('payment', 'reason', 'date')


class PaymentTagAdmin(admin.ModelAdmin):
    list_display = ('user', 'tag')


admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.PaymentInvalid, PaymentInvalidAdmin)
admin.site.register(models.PaymentTag, PaymentTagAdmin)
