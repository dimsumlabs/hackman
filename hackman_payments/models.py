from django.conf import settings
from django.db import models


class PaymentTag(models.Model):
    """Map tags in git payment repo to users"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    tag = models.CharField(max_length=50, db_index=True)
