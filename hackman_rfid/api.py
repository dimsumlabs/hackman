from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
import importlib
import hashlib

from . import models

__all__ = ['cards_read', 'card_validate', 'card_pair']


def _make_cache_key(card_hash: str) -> str:
    return 'rfid_card_{}'.format(card_hash)


def cards_read():
    """Yield hashed cards from configured backend"""

    impl = importlib.import_module(settings.RFID_READER['BACKEND'])
    hash_salt = settings.RFID_READER['HASH_SALT']

    for card in impl.get_cards():
        # Double hash with salt
        cardhash = hashlib.sha256(
            b''.join((
                hashlib.sha256(card).hexdigest().encode('ascii'),
                hash_salt.encode('ascii')
            ))
        ).hexdigest()
        yield (cardhash, card)


def card_validate(card_hash: str) -> User:
    """Validate card hash and return associated user
    Will create RFIDCard if it doesnt already exist"""

    cache_key = _make_cache_key(card_hash)
    c = cache.get(cache_key)

    if not c:
        c, _ = models.RFIDCard.objects.get_or_create(rfid_hash=card_hash)
        cache.set(cache_key, c)

    if not c.revoked:
        return c


def card_pair(user_id: int, card_id: int) -> models.RFIDCard:
    card = models.RFIDCard.objects.get(id=card_id)
    if card.user:
        raise ValueError("Card cannot be paired to another user")

    card.user = get_user_model().objects.get(id=user_id)
    card.save()

    return card


def card_get(card_id: int) -> models.RFIDCard:
    try:
        return models.RFIDCard.objects.get(id=card_id)
    except models.RFIDCard.DoesNotExist:
        return None
