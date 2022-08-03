from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from .models import PaymentTag
import calendar

from .enums import PaymentGrade


def _get_now():
    """Simple functionality but have to wrap up in function to test"""
    return datetime.utcnow().date()


def tags_not_matching():
    """Return all tags not matching any user"""
    return [
        ":".join(t)
        for t in PaymentTag.objects.filter(user=None).values_list("hashtag", "tag")
    ]


def get_valid_until(user_id: int) -> str:
    # TODO - return a datetime
    r = get_redis_connection("default")
    valid_until = r.get("payment_user_id_{}".format(user_id))
    if valid_until is None:
        return None

    valid_until = datetime.strptime(
        valid_until.decode("utf8"), "%Y-%m-%dT%H:%M:%S"
    ).date()
    # FIXME - we only know to month accuracy the payment details, so
    # returning a full date is wrong
    return valid_until


def has_paid(user_id: int) -> bool:

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


def unpaid_users():
    """Yield all user ids that have not paid in advance"""

    for uid in get_user_model().objects.all().values_list("id", flat=True):
        if has_paid(uid) != PaymentGrade.PAID:
            yield uid


def payment_reminder_email_format():
    now = _get_now()
    cur = date(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
    next_month_date = cur + timedelta(days=1)
    month_name = calendar.month_name[next_month_date.month]

    return render_to_string("payment_reminder.jinja2", context={"month": month_name})


def payment_submit(user_id: int, year: int, month: int, _redis_pipe=None) -> int:

    valid_until = datetime(year, month, calendar.monthrange(year, month)[1], 23, 59)

    r = _redis_pipe or get_redis_connection("default")
    r.set("payment_user_id_{}".format(user_id), valid_until.isoformat())
    # FIXME - we only know to month accuracy the payment details, so
    # storing a full datetime is wrong
