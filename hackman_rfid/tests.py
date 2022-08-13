from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import hashlib
import pytest
import os

from hackman_rfid import models
from hackman_rfid import api


@pytest.fixture
def card_user() -> User:
    user, _ = get_user_model().objects.get_or_create(username="testhesten")
    return user  # type: ignore


@pytest.fixture
def random_card() -> models.RFIDCard:
    card_hash = hashlib.sha256(os.urandom(10)).hexdigest()
    return models.RFIDCard.objects.create(rfid_hash=card_hash)  # type: ignore


@pytest.fixture
def paired_card(card_user: User) -> models.RFIDCard:
    user = card_user
    card_hash = hashlib.sha256(os.urandom(10)).hexdigest()
    return models.RFIDCard.objects.create(rfid_hash=card_hash, user=user)  # type: ignore


def test_get_cards() -> None:
    _cards = api.cards_read()
    cards = [next(_cards) for _ in range(3)]

    # Assert card is hashed with sha256
    assert len(cards[0][0]) == 64


@pytest.mark.django_db
def test_card_validate_db_entry_created() -> None:
    """Is a new card entry created on validation"""
    card_hash = hashlib.sha256(os.urandom(10)).hexdigest()
    api.card_validate(card_hash)

    assert len(models.RFIDCard.objects.all()) == 1


@pytest.mark.django_db
def test_card_validate_no_user(random_card: models.RFIDCard) -> None:
    """Check access attempt without a user"""

    card = api.card_validate(random_card.rfid_hash)

    assert card.user_id is None  # type: ignore
    c = models.RFIDCard.objects.get(rfid_hash=random_card.rfid_hash)
    assert c.id == random_card.id


@pytest.mark.django_db
def test_card_validate_user(paired_card: models.RFIDCard, card_user: User) -> None:
    """Check that validate returns correct user if user is associated"""
    user = api.card_validate(paired_card.rfid_hash)
    assert user.id == card_user.id  # type: ignore


@pytest.mark.django_db
def test_card_pair_no_card() -> None:
    """Test to pair with a nonexistent card id"""
    with pytest.raises(models.RFIDCard.DoesNotExist):
        api.card_pair(1, 1)


@pytest.mark.django_db
def test_card_pair_no_user(random_card: models.RFIDCard) -> None:
    """Test to pair with a nonexistent user id"""

    with pytest.raises(get_user_model().DoesNotExist):
        api.card_pair(1, random_card.id)


@pytest.mark.django_db
def test_card_pair_already_paired(
    card_user: User, paired_card: models.RFIDCard
) -> None:
    with pytest.raises(ValueError):
        api.card_pair(card_user.id, paired_card.id)  # type: ignore


@pytest.mark.django_db
def test_card_pair(card_user: User, random_card: models.RFIDCard) -> None:
    c = api.card_pair(card_user.id, random_card.id)  # type: ignore
    assert isinstance(c, models.RFIDCard)
    assert c.id == random_card.id
    assert c.user.id == card_user.id  # type: ignore


@pytest.mark.django_db
def test_card_get(random_card: models.RFIDCard) -> None:
    c1 = api.card_get(random_card.id)
    c2 = api.card_get(31337)
    assert isinstance(c1, models.RFIDCard)
    assert c1.id == random_card.id
    assert c2 is None
