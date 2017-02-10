from django.conf import settings
from django.db import models


class Payment(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    payment_date = models.DateTimeField(auto_now_add=True, db_index=True)
    valid_until = models.DateField(db_index=True)

    def __str__(self):
        return ' - '.join((
            str(self.user.username),
            self.valid_until.isoformat()
        ))


class PaymentInvalid(models.Model):

    payment = models.OneToOneField(Payment)
    reason = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)


class PaymentTag(models.Model):
    """Map tags in git payment repo to users"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    tag = models.CharField(max_length=50, db_index=True)
