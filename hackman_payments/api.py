from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from .models import PaymentTag
import calendar
import typing
from typing import (
    Generator,
    Optional,
    List,
)

from .enums import PaymentGrade


def _get_now() -> date:
    """Simple functionality but have to wrap up in function to test"""
    return datetime.utcnow().date()


def tags_not_matching() -> List[str]:
    """Return all tags not matching any user"""
    return [
        ":".join(t)
        for t in PaymentTag.objects.filter(user=None).values_list("hashtag", "tag")
    ]


def get_valid_until(user_id: int) -> Optional[date]:
    # TODO - return a datetime
    r = get_redis_connection("default")
    valid_until = r.get("payment_user_id_{}".format(user_id))
    if valid_until is None:
        return None

    return datetime.strptime(valid_until.decode("utf8"), "%Y-%m-%dT%H:%M:%S").date()


def has_paid(user_id: int) -> PaymentGrade:

    if is_within_grace_period(user_id):
        return PaymentGrade.GRACE

    r = get_redis_connection("default")
    user_model = get_user_model()

    user_active = r.get("user_active_{}".format(user_id))

    if user_active is None:
        u = user_model.objects.get(id=user_id)
        r.set("user_active_{}".format(user_id), bytes(u.is_active), ex=3600 * 24)

        if not u.is_active:
            return PaymentGrade.NOT_PAID

    elif not bool(user_active):
        return PaymentGrade.NOT_PAID

    valid_until = get_valid_until(user_id)
    if valid_until is None:
        return PaymentGrade.NOT_PAID

    now = _get_now()
    if valid_until < now and valid_until + timedelta(weeks=2) >= now:
        return PaymentGrade.GRACE

    elif valid_until >= now:
        return PaymentGrade.PAID

    else:
        return PaymentGrade.NOT_PAID


def is_within_grace_period(user_id: int) -> bool:
    r = get_redis_connection("default")
    user_claim_grace_at = r.get(f"user_claim_grace_{user_id}")

    if not user_claim_grace_at:
        return False

    user_claim_grace_at = user_claim_grace_at.decode("utf-8")
    try:
        claim_at = datetime.strptime(user_claim_grace_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        print(claim_at, datetime.utcnow())
        if claim_at <= datetime.utcnow() and datetime.utcnow() <= claim_at + timedelta(
            minutes=1
        ):
            return True
        else:
            return False
    except (TypeError, ValueError) as e:
        print("warning: parse error for grace period for user", user_id, e)
        return False


def unpaid_users() -> Generator[User, None, None]:
    """Yield all user ids that have not paid in advance"""

    for uid in get_user_model().objects.all().values_list("id", flat=True):
        if has_paid(uid) != PaymentGrade.PAID:
            yield uid


def payment_reminder_email_format() -> str:
    now = _get_now()
    cur = date(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
    next_month_date = cur + timedelta(days=1)
    month_name = calendar.month_name[next_month_date.month]

    return render_to_string("payment_reminder.jinja2", context={"month": month_name})


def payment_submit(
    user_id: int, year: int, month: int, _redis_pipe: typing.Any = None
) -> None:

    valid_until = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59)

    r = _redis_pipe or get_redis_connection("default")
    r.set("payment_user_id_{}".format(user_id), valid_until.isoformat())
    # FIXME - we only know to month accuracy the payment details, so
    # storing a full datetime is wrong


def payment_claim(
    user_id: int, year: int, month: int, _redis_pipe: typing.Any = None
) -> None:
    if year == datetime.now().year and month == datetime.now().month:
        r = _redis_pipe or get_redis_connection("default")
        r.set(f"user_claim_grace_{user_id}", f"{datetime.utcnow().isoformat()}Z")
    else:
        pass
        # supposedly I should log someone's payment-claim.
