from django.template.loader import render_to_string
from datetime import datetime, timedelta, date
from django.db.models import Max
from decimal import Decimal
import calendar

from .enums import PaymentGrade
from .models import Payment


def _get_next_month():
    now = datetime.utcnow()
    cur = date(now.year, now.month,
               calendar.monthrange(now.year, now.month)[1])
    return (cur+timedelta(days=1))


def has_paid(user_id: int) -> bool:
    qs = Payment.objects.all()
    qs = qs.filter(user_id=user_id)
    qs = qs.filter(paymentinvalid=None)

    # Grace period for payments
    now = datetime.utcnow()
    qs = qs.filter(valid_until__gt=(now-timedelta(weeks=2)))
    qs = qs.order_by('payment_date')
    payment = qs.first()

    if not payment:
        return PaymentGrade.NOT_PAID

    elif payment.valid_until < now.date():
        return PaymentGrade.GRACE

    else:
        return PaymentGrade.PAID


def unpaid_users():
    """Yield all user ids that have not paid in advance"""

    next_month_date = _get_next_month()

    qs = Payment.objects.filter(paymentinvalid__isnull=True)
    qs = qs.values('user_id')
    qs = qs.annotate(valid_until=Max('valid_until'))

    for o in qs:
        if o['valid_until'] <= next_month_date:
            yield o['user_id']


def payment_reminder_email_format():  # pragma: no cover
    next_month_date = _get_next_month()
    month_name = calendar.month_name[next_month_date.month]

    return render_to_string('payment_reminder.jinja2', context={
        'month': month_name
    })


def payment_submit(user_id: int, year: int, month: int,
                   amount: Decimal) -> int:

    valid_until = datetime(year, month,
                           calendar.monthrange(year, month)[1],
                           23, 59)

    return Payment.objects.create(
        user_id=user_id,
        amount=amount,
        valid_until=valid_until).id
