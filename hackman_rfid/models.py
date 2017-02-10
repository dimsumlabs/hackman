from django.conf import settings
from django.db import models


class RFIDCard(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             default=None)

    rfid_hash = models.CharField(max_length=64, db_index=True)
    revoked = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return ' - '.join((
            self.user.username,
            self.rfid_hash
        ))


class RFIDLog(models.Model):

    card = models.ForeignKey(RFIDCard)
    time = models.DateTimeField(auto_now_add=True, db_index=True)
