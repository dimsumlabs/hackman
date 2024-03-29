from django.conf import settings
from django.db import models
import typing


class PaymentTag(models.Model):
    """Map tags in git payment repo to users"""

    id = models.AutoField(primary_key=True)  # type: ignore

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )  # type: ignore
    hashtag = models.CharField(max_length=20, db_index=True, default="dues")  # type: ignore
    tag = models.CharField(max_length=50, db_index=True, null=False, blank=True)  # type: ignore

    def make_key(self) -> str:
        if self.tag:
            return "{}:{}".format(self.hashtag, self.tag)
        else:
            return typing.cast(str, self.hashtag)
