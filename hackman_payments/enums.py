from enum import Enum


class PaymentGrade(Enum):
    NOT_PAID = 0
    GRACE = 1
    PAID = 2
