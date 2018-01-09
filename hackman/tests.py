from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, date
from django_redis import get_redis_connection
from unittest import mock
import hashlib
import pytest
import json

from . import views
from . import rest_api
from . import api as hackman_api


# BEGIN VIEW TESTS

@pytest.fixture
def auth_user():
    user = get_user_model().objects.create_user(
        username='testhesten',
        password='testpass')
    return user


@pytest.fixture
def paid_user():
    from hackman_payments import api as payment_api

    next_month = datetime.utcnow()+timedelta(days=32)

    user = get_user_model().objects.create_user(
        username='testhesten_paid',
        password='testpass')
    payment_api.payment_submit(user.id,
                               next_month.year,
                               next_month.month)
    yield user
    get_redis_connection('default').flushall()


@pytest.fixture
def not_paid_user():
    user = get_user_model().objects.create_user(
        username='testhesten_notpaid',
        password='testpass')
    return user


@pytest.fixture
def card_unpaired():
    from hackman_rfid import models as rfid_models
    return rfid_models.RFIDCard.objects.create(
        rfid_hash=hashlib.sha256(b'test').hexdigest())


@pytest.fixture
def card_paired(paid_user):
    from hackman_rfid import models as rfid_models
    return (paid_user, rfid_models.RFIDCard.objects.create(
        user=paid_user,
        rfid_hash=hashlib.sha256(b'test').hexdigest()))


def inject_session(request, user=None):
    """Helper method for creating associated session to request
    Will modify request but also return it for convenience"""
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    request.user = user

    return request


def test_login_get(rf):
    request = rf.get('/login/')
    response = views.login(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_post_user_exist(rf, auth_user):
    request = inject_session(rf.post('/login/', {
        'username': 'testhesten',
        'password': 'testpass'
    }))
    response = views.login(request)
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
def test_login_post_user_not_exist(rf):
    request = rf.post('/login/', {
        'username': 'testhesten',
        'password': 'my_password'
    })
    response = views.login(request)
    assert response.status_code == 400


def test_account_create_non_post(rf):
    request = rf.get('/account_create/')
    response = views.account_create(request)
    assert response.status_code == 400


def test_account_create_nonlocal_ip(rf):
    request = rf.post('/account_create/', REMOTE_ADDR='8.8.8.8')
    response = views.account_create(request)
    assert response.status_code == 403


def test_account_create_form_invalid(rf):
    request = rf.post('/account_create/', {
        'err_field': 'not an email',
        'password': 'not a real password'
    })
    response = views.account_create(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_account_create_invalid_email(rf):
    request = inject_session(rf.post('/account_create/', {
        'email': 'testhesten',
        'password': 'not a real password'
    }))
    response = views.account_create(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_account_create(rf):
    request = inject_session(rf.post('/account_create/', {
        'email': 'test@hest.se',
        'password': 'not a real password'
    }))
    response = views.account_create(request)
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
def test_door_open_paid(rf, paid_user):
    m = mock.Mock()
    request = inject_session(rf.get('/door_open/'), user=paid_user)
    response = views.door_open(request, _door_api=m)
    assert response.status_code == 302
    assert response.url == '/'
    assert m.open.called is True


@pytest.mark.django_db
def test_door_open_not_paid(rf, not_paid_user):
    request = inject_session(rf.get('/door_open/'), user=not_paid_user)
    response = views.door_open(request)
    assert response.status_code == 403


@pytest.mark.django_db
def test_rfid_pair_non_post(rf, paid_user):
    request = inject_session(rf.get('/rfid_pair/'), user=paid_user)
    response = views.rfid_pair(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_rfid_pair_form_error(rf, paid_user):
    request = inject_session(rf.post('/rfid_pair/', {
        'err_field': 'didum'
    }), user=paid_user)
    response = views.rfid_pair(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_rfid_pair_card_unpaired(rf, paid_user, card_unpaired):
    request = inject_session(rf.post('/rfid_pair/', {
        'card_id': str(card_unpaired.id)
    }), user=paid_user)

    response = views.rfid_pair(request)
    assert response.status_code == 302


@pytest.mark.django_db
def test_rfid_pair_card_paired(rf, card_paired):
    user, card_paired = card_paired
    request = inject_session(rf.post('/rfid_pair/', {
        'card_id': str(card_paired.id)
    }), user=user)

    response = views.rfid_pair(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_submit_non_post(rf, paid_user):
    request = inject_session(rf.get('/payment_submit/'), user=paid_user)
    response = views.payment_submit(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_submit_form_invalid(rf, paid_user):
    request = inject_session(rf.post('/payment_submit/', {
        'not_exist_field': 'hallo',
    }), user=paid_user)
    response = views.payment_submit(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_submit(rf, not_paid_user):
    now = datetime.utcnow()
    request = inject_session(rf.post('/payment_submit/', {
        'year_month': '{year}-{month:02d}'.format(year=now.year,
                                                  month=now.month),
    }), user=not_paid_user)
    response = views.payment_submit(request, r=True)
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
def test_tags_not_matching(rf):
    with mock.patch('hackman_payments.api.tags_not_matching',
                    return_value=['dues:somedude']):

        request = rf.get('/api/v1/tags_not_matching/')
        response = rest_api.tags_not_matching(request)
        assert response.status_code == 200
        assert json.loads(response.content.decode()) == ['dues:somedude']


# END VIEW TESTS

# BEGIN API TESTS


@pytest.fixture
def user_paid():
    from hackman_payments import api as payments_api
    user = get_user_model().objects.create(username='testhesten_fullpay')
    payments_api.payment_submit(user.id, 2017, 2)
    yield user
    get_redis_connection('default').flushall()


@pytest.fixture
def user_paid_grace():
    from hackman_payments import api as payments_api
    user = get_user_model().objects.create(username='testhesten_gracepay')
    payments_api.payment_submit(user.id, 2017, 1)
    yield user
    get_redis_connection('default').flushall()


@pytest.fixture
def user_not_paid():
    user = get_user_model().objects.create(username='testhesten_nopayment')
    return user


@pytest.mark.django_db
def test_has_paid_has_paid(user_paid):
    with mock.patch('hackman_payments.api._get_now',
                    return_value=date(2017, 2, 20)):
        ret = hackman_api.door_open_if_paid(user_paid.id,
                                            _door_api=mock.Mock())
        assert ret is True


@pytest.mark.django_db
def test_has_paid_has_paid_grace(user_paid_grace):
    with mock.patch('hackman_payments.api._get_now',
                    return_value=date(2017, 2, 12)):
        ret = hackman_api.door_open_if_paid(user_paid_grace.id,
                                            _door_api=mock.Mock())
        assert ret is True


@pytest.mark.django_db
def test_has_paid_has_not_paid(user_not_paid):
    ret = hackman_api.door_open_if_paid(user_not_paid.id,
                                        _door_api=mock.Mock())
    assert ret is False


# END API TESTS
