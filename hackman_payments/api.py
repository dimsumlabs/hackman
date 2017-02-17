from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
import calendar

from .enums import PaymentGrade


def _get_now():
    """Simple functionality but have to wrap up in function to test"""
    return datetime.utcnow().date()


def has_paid(user_id: int) -> bool:

    r = get_redis_connection('default')
    valid_until = r.get('payment_user_id_{}'.format(user_id))
    if valid_until is None:
        return PaymentGrade.NOT_PAID

    valid_until = datetime.strptime(
        valid_until.decode('utf8'), '%Y-%m-%dT%H:%M:%S').date()

    now = _get_now()
    if valid_until < now and valid_until+timedelta(weeks=2) >= now:
        return PaymentGrade.GRACE

    elif valid_until >= now:
        return PaymentGrade.PAID

    else:
        return PaymentGrade.NOT_PAID


def unpaid_users():
    """Yield all user ids that have not paid in advance"""

    for uid in get_user_model().objects.all().values_list('id', flat=True):
        if has_paid(uid) != PaymentGrade.PAID:
            yield uid


def payment_reminder_email_format():  # pragma: no cover
    now = _get_now()
    cur = date(now.year, now.month,
               calendar.monthrange(now.year, now.month)[1])
    next_month_date = (cur+timedelta(days=1))
    month_name = calendar.month_name[next_month_date.month]

    return render_to_string('payment_reminder.jinja2', context={
        'month': month_name
    })


def payment_submit(user_id: int, year: int, month: int,
                   _redis_pipe=None) -> int:

    valid_until = datetime(year, month,
                           calendar.monthrange(year, month)[1],
                           23, 59)

    r = _redis_pipe or get_redis_connection('default')
    r.set('payment_user_id_{}'.format(user_id), valid_until.isoformat())
