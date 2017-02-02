from django.conf import settings
from django.db import models


class Payment(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    amount = models.DecimalField(max_digits=5, decimal_places=2)

    payment_date = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateField()


class PaymentInvalid(models.Model):

    payment = models.OneToOneField(Payment)
    reason = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
