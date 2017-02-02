# from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from decimal import Decimal
import calendar

from .enums import PaymentGrade
from .models import Payment


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


def payment_submit(user_id: int, year: int, month: int,
                   amount: Decimal) -> int:

    valid_until = datetime(year, month,
                           calendar.monthrange(year, month)[1],
                           23, 59)

    return Payment.objects.create(
        user_id=user_id,
        amount=amount,
        valid_until=valid_until).id
