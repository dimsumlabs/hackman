from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import pytest

from . import api as payment_api
from .enums import PaymentGrade
from .models import Payment


@pytest.fixture
def user_paid():
    user = get_user_model().objects.create(username='testhesten-paid')
    Payment.objects.create(
        user=user,
        valid_until=(datetime.utcnow()+timedelta(days=30)))
    return user


@pytest.fixture
def user_paid_grace():
    user = get_user_model().objects.create(username='testhesten-grace')
    Payment.objects.create(
        user=user,
        valid_until=(datetime.utcnow()-timedelta(days=1)))
    return user


@pytest.fixture
def user_not_paid():
    user = get_user_model().objects.create(username='testhesten-notpaid')
    Payment.objects.create(
        user=user,
        valid_until=(datetime.utcnow()-timedelta(days=60)))
    return user


@pytest.mark.django_db
def test_has_paid_has_paid(user_paid):
    paid = payment_api.has_paid(user_paid.id)
    assert paid == PaymentGrade.PAID


@pytest.mark.django_db
def test_has_paid_has_paid_grace(user_paid_grace):
    paid = payment_api.has_paid(user_paid_grace.id)
    assert paid == PaymentGrade.GRACE


@pytest.mark.django_db
def test_has_paid_has_not_paid(user_not_paid):
    paid = payment_api.has_paid(user_not_paid.id)
    assert paid == PaymentGrade.NOT_PAID


@pytest.mark.django_db
def test_unpaid_users(user_paid, user_paid_grace, user_not_paid):
    unpaid_users = list(payment_api.unpaid_users())
    assert len(unpaid_users) == 2
    assert user_paid.id not in unpaid_users
    assert user_paid_grace.id in unpaid_users
    assert user_not_paid.id in unpaid_users
