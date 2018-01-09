from django.contrib.auth import get_user_model
from hackman_payments.models import PaymentTag
from django_redis import get_redis_connection
from datetime import date
from unittest import mock
import pytest

from . import api as payment_api
from .enums import PaymentGrade


@pytest.fixture
def paymenttag_no_user():
    yield PaymentTag.objects.create(
        user=None,
        hashtag='dues',
        tag='somedude')


@pytest.fixture
def user_paid():
    user = get_user_model().objects.create(username='testhesten-paid',
                                           email='p@test.se')
    payment_api.payment_submit(user.id, 2017, 2)
    yield user
    get_redis_connection('default').flushall()


@pytest.fixture
def user_paid_grace():
    user = get_user_model().objects.create(username='testhesten-grace',
                                           email='g@test.se')
    payment_api.payment_submit(user.id, 2017, 1)
    yield user
    get_redis_connection('default').flushall()


@pytest.fixture
def user_not_paid():
    user = get_user_model().objects.create(username='testhesten-notpaid',
                                           email='np@test.se')
    payment_api.payment_submit(user.id, 2016, 12)
    yield user
    get_redis_connection('default').flushall()


@pytest.fixture
def user_not_active():
    user = get_user_model().objects.create(username='testhesten-notactive',
                                           email='na@test.se')
    user.is_active = False
    user.save()
    payment_api.payment_submit(user.id, 2016, 12)
    yield user
    get_redis_connection('default').flushall()


@pytest.mark.django_db
def test_non_matching_user(paymenttag_no_user):
    tags = payment_api.tags_not_matching()
    assert tags == ['dues:somedude']


@pytest.mark.django_db
def test_has_paid_has_paid(user_paid):
    with mock.patch('hackman_payments.api._get_now',
                    return_value=date(2017, 2, 20)):
        paid = payment_api.has_paid(user_paid.id)
        assert paid == PaymentGrade.PAID


@pytest.mark.django_db
def test_has_paid_has_paid_grace(user_paid_grace):
    with mock.patch('hackman_payments.api._get_now',
                    return_value=date(2017, 2, 12)):
        paid = payment_api.has_paid(user_paid_grace.id)
        assert paid == PaymentGrade.GRACE


@pytest.mark.django_db
def test_has_paid_has_not_paid(user_not_paid):
    paid = payment_api.has_paid(user_not_paid.id)
    assert paid == PaymentGrade.NOT_PAID


@pytest.mark.django_db
def test_has_paid_not_active(user_not_active):
    paid = payment_api.has_paid(user_not_active.id)
    assert paid == PaymentGrade.NOT_PAID

    # Test again to check for cached
    paid = payment_api.has_paid(user_not_active.id)
    assert paid == PaymentGrade.NOT_PAID


@pytest.mark.django_db
def test_unpaid_users(user_paid, user_paid_grace, user_not_paid):
    with mock.patch('hackman_payments.api._get_now',
                    return_value=date(2017, 2, 1)):

        unpaid_users = list(payment_api.unpaid_users())
        assert len(unpaid_users) == 2
        assert user_paid.id not in unpaid_users
        assert user_paid_grace.id in unpaid_users
        assert user_not_paid.id in unpaid_users
