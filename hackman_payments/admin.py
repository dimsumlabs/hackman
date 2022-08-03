from django.contrib import admin

from . import models


class PaymentTagAdmin(admin.ModelAdmin):
    list_display = ("user", "hashtag", "tag")


admin.site.register(models.PaymentTag, PaymentTagAdmin)
