from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import transaction
from django.conf import settings
import importlib
import hashlib

from . import models

__all__ = ['cards_read', 'card_validate', 'card_pair']


def cards_read():
    """Yield hashed cards from configured backend"""

    impl = importlib.import_module(settings.RFID_READER['BACKEND'])
    hash_salt = settings.RFID_READER['HASH_SALT']

    for card in impl.get_cards():
        yield hashlib.sha256(b''.join((  # Double hash with salt
            hashlib.sha256(card).hexdigest().encode('ascii'),
            hash_salt.encode('ascii')))).hexdigest()


def card_validate(card_hash: str) -> User:
    """Validate card hash and return associated user
    Will create RFIDCard if it doesnt already exist"""

    with transaction.atomic():
        c, _ = models.RFIDCard.objects.get_or_create(rfid_hash=card_hash)
        models.RFIDLog.objects.create(card_id=c.id)

    if not c.revoked:
        return c.user


def card_pair(user_id: int, card_id: int) -> models.RFIDCard:
    card = models.RFIDCard.objects.get(id=card_id)
    if card.user:
        raise ValueError("Card cannot be paired to another user")

    card.user = get_user_model().objects.get(id=user_id)
    card.save()

    return card


def access_last(paired=None):
    qs = models.RFIDLog.objects.all()

    if paired is None:
        pass

    elif paired:
        qs = qs.filter(card__user__isnull=False)

    else:
        qs = qs.filter(card__user__isnull=True)

    return qs.order_by('-time').first().card
