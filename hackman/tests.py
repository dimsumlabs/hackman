from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import RequestFactory
from django.http import HttpRequest
from datetime import datetime, timedelta, date
from django_redis import get_redis_connection
from unittest import mock
import hashlib
import pytest
import typing
from hackman_rfid import models as rfid_models


from . import views
from . import api as hackman_api


# BEGIN VIEW TESTS


@pytest.fixture
def auth_user() -> User:
    user = get_user_model().objects.create_user(  # type: ignore
        username="testhesten", password="testpass"
    )
    return typing.cast(User, user)


@pytest.fixture
def paid_user() -> typing.Generator[User, None, None]:
    from hackman_payments import api as payment_api

    next_month = datetime.utcnow() + timedelta(days=32)

    user = get_user_model().objects.create_user(  # type: ignore
        username="testhesten_paid", password="testpass"
    )
    payment_api.payment_submit(user.id, next_month.year, next_month.month)
    yield user
    get_redis_connection("default").flushall()


@pytest.fixture
def not_paid_user() -> User:
    user = get_user_model().objects.create_user(  # type: ignore
        username="testhesten_notpaid", password="testpass"
    )
    return typing.cast(User, user)


@pytest.fixture
def card_unpaired() -> rfid_models.RFIDCard:
    return typing.cast(
        rfid_models.RFIDCard,
        rfid_models.RFIDCard.objects.create(
            rfid_hash=hashlib.sha256(b"test").hexdigest()
        ),
    )


@pytest.fixture
def card_paired(paid_user: User) -> typing.Tuple[User, rfid_models.RFIDCard]:
    return (
        paid_user,
        rfid_models.RFIDCard.objects.create(
            user=paid_user, rfid_hash=hashlib.sha256(b"test").hexdigest()
        ),
    )


def inject_session(
    request: HttpRequest, user: typing.Optional[User] = None
) -> HttpRequest:
    """Helper method for creating associated session to request
    Will modify request but also return it for convenience"""

    get_response = mock.MagicMock()

    middleware = SessionMiddleware(get_response)
    middleware.process_request(request)
    request.session.save()

    if user:
        request.user = user

    return request


def test_login_get(rf: RequestFactory) -> None:
    request = rf.get("/login/")
    response = views.login(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_post_user_exist(rf: RequestFactory, auth_user: User) -> None:
    request = inject_session(
        rf.post("/login/", {"username": "testhesten", "password": "testpass"})
    )
    response = views.login(request)
    assert response.status_code == 302
    assert response.url == "/"


@pytest.mark.django_db
def test_login_post_user_not_exist(rf: RequestFactory) -> None:
    request = rf.post("/login/", {"username": "testhesten", "password": "my_password"})
    response = views.login(request)
    assert response.status_code == 400


def test_account_create_non_post(rf: RequestFactory) -> None:
    request = rf.get("/account_create/")
    response = views.account_create(request)
    assert response.status_code == 200


def test_account_create_nonlocal_ip(rf: RequestFactory) -> None:
    request = rf.post("/account_create/", REMOTE_ADDR="8.8.8.8")
    response = views.account_create(request)
    assert response.status_code == 403


def test_account_create_form_invalid(rf: RequestFactory) -> None:
    request = rf.post(
        "/account_create/",
        {"err_field": "not an email", "password": "not a real password"},
    )
    response = views.account_create(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_account_create_invalid_email(rf: RequestFactory) -> None:
    request = inject_session(
        rf.post(
            "/account_create/",
            {"email": "testhesten", "password": "not a real password"},
        )
    )
    response = views.account_create(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_account_create(rf: RequestFactory) -> None:
    request = inject_session(
        rf.post(
            "/account_create/",
            {"email": "test@hest.se", "password": "not a real password"},
        )
    )
    response = views.account_create(request)
    assert response.status_code == 302
    assert response.url == "/"  # type: ignore


@pytest.mark.django_db
def test_door_open_paid(rf: RequestFactory, paid_user: User) -> None:
    m = mock.Mock()
    request = inject_session(rf.get("/door_open/"), user=paid_user)
    response = views.door_open(request, _door_api=m)
    assert response.status_code == 302
    assert response.url == "/"  # type: ignore
    assert m.open.called is True


@pytest.mark.django_db
def test_door_open_not_paid(rf: RequestFactory, not_paid_user: User) -> None:
    request = inject_session(rf.get("/door_open/"), user=not_paid_user)
    response = views.door_open(request)
    assert response.status_code == 403


@pytest.mark.django_db
def test_rfid_pair_non_post(rf: RequestFactory, paid_user: User) -> None:
    request = inject_session(rf.get("/rfid_pair/"), user=paid_user)
    response = views.rfid_pair(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_account_actions(rf: RequestFactory, paid_user: User) -> None:
    request = inject_session(rf.get("/account_actions/"), user=paid_user)
    response = views.account_actions(request)
    assert response.status_code == 200


@pytest.mark.django_db
def test_rfid_pair_form_error(rf: RequestFactory, paid_user: User) -> None:
    request = inject_session(
        rf.post("/rfid_pair/", {"err_field": "didum"}), user=paid_user
    )
    response = views.rfid_pair(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_rfid_pair_card_unpaired(
    rf: RequestFactory, paid_user: User, card_unpaired: rfid_models.RFIDCard
) -> None:
    request = inject_session(
        rf.post("/rfid_pair/", {"card_id": str(card_unpaired.id)}), user=paid_user
    )

    response = views.rfid_pair(request)
    assert response.status_code == 302


@pytest.mark.django_db
def test_rfid_pair_card_paired(
    rf: RequestFactory, card_paired: typing.Tuple[User, rfid_models.RFIDCard]
) -> None:
    user: User
    card: rfid_models.RFIDCard
    user, card = card_paired
    request = inject_session(
        rf.post("/rfid_pair/", {"card_id": str(card.id)}), user=user
    )

    response = views.rfid_pair(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_submit_non_post(rf: RequestFactory, paid_user: User) -> None:
    request = inject_session(rf.get("/payment_submit/"), user=paid_user)
    response = views.payment_submit(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_submit_form_invalid(rf: RequestFactory, paid_user: User) -> None:
    request = inject_session(
        rf.post(
            "/payment_submit/",
            {
                "not_exist_field": "hallo",
            },
        ),
        user=paid_user,
    )
    response = views.payment_submit(request)
    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_submit(rf: RequestFactory, not_paid_user: User) -> None:
    now = datetime.utcnow()
    request = inject_session(
        rf.post(
            "/payment_submit/",
            {
                "year_month": "{year}-{month:02d}".format(
                    year=now.year, month=now.month
                ),
            },
        ),
        user=not_paid_user,
    )
    response = views.payment_submit(request, r=True)
    assert response.status_code == 200


# END VIEW TESTS

# BEGIN API TESTS


@pytest.fixture
def user_paid() -> typing.Generator[User, None, None]:
    from hackman_payments import api as payments_api

    user = get_user_model().objects.create(username="testhesten_fullpay")
    payments_api.payment_submit(user.id, 2017, 2)
    yield user
    get_redis_connection("default").flushall()


@pytest.fixture
def user_paid_grace() -> typing.Generator[User, None, None]:
    from hackman_payments import api as payments_api

    user = get_user_model().objects.create(username="testhesten_gracepay")
    payments_api.payment_submit(user.id, 2017, 1)
    yield user
    get_redis_connection("default").flushall()


@pytest.fixture
def user_not_paid() -> User:
    user = get_user_model().objects.create(username="testhesten_nopayment")
    return typing.cast(User, user)


@pytest.mark.django_db
def test_has_paid_has_paid(user_paid: User) -> None:
    with mock.patch("hackman_payments.api._get_now", return_value=date(2017, 2, 20)):
        user_id: int = user_paid.id  # type: ignore
        ret = hackman_api.door_open_if_paid(user_id, _door_api=mock.Mock())
        assert ret is True


@pytest.mark.django_db
def test_has_paid_has_paid_grace(user_paid_grace: User) -> None:
    with mock.patch("hackman_payments.api._get_now", return_value=date(2017, 2, 12)):
        user_id: int = user_paid_grace.id  # type: ignore
        ret = hackman_api.door_open_if_paid(user_id, _door_api=mock.Mock())
        assert ret is True


@pytest.mark.django_db
def test_has_paid_has_not_paid(user_not_paid: User) -> None:
    user_id: int = user_not_paid.id  # type: ignore
    ret = hackman_api.door_open_if_paid(user_id, _door_api=mock.Mock())
    assert ret is False


# END API TESTS
