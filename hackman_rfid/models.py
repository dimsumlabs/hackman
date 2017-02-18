from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache

from django.conf import settings
from django.db import models


class RFIDCard(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                             default=None)

    rfid_hash = models.CharField(max_length=64, db_index=True)
    revoked = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return ' - '.join((
            self.user.username if self.user else 'unpaired',
            self.rfid_hash
        ))


@receiver(post_save, sender=RFIDCard)
def invalidate_card(sender, instance, **kwargs):
    from .api import _make_cache_key
    cache.set(_make_cache_key(instance.rfid_hash), instance)
