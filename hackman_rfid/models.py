from django.conf import settings
from django.db import models


class RFIDCard(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             default=None)

    rfid_hash = models.CharField(max_length=512, db_index=True)
    revoked = models.BooleanField(default=False)


class RFIDLog(models.Model):

    card = models.ForeignKey(RFIDCard)
    time = models.DateTimeField(auto_now_add=True)
