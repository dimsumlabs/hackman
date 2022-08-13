from hackman_notifier import api as notification_api
from hackman_payments import enums as payment_enums
from hackman_payments import api as payment_api
from hackman_door import api as door_api
import typing
import json


def door_open_if_paid(
    user_id: int,
    _door_api: typing.Any = None,
    source: str = "UNKNOWN",
    user_name: typing.Optional[str] = None,
    rawdata: typing.Optional[bytes] = None,
) -> bool:
    """Open door if paid and send pubsub notification accordingly"""
    paid = payment_api.has_paid(user_id)
    paid_grade = payment_enums.PaymentGrade(paid).name

    log: typing.Dict[str, typing.Union[str, int]] = {}

    if paid_grade == "PAID":
        (_door_api or door_api).open()
        log["event"] = "DOOR_OPEN"
        ret = True

    elif paid_grade == "GRACE":
        (_door_api or door_api).open()
        log["event"] = "DOOR_OPEN_GRACE"
        ret = True

    else:
        log["event"] = "DOOR_OPEN_DENIED"
        ret = False

    if source:
        log["source"] = source

    if rawdata:
        log["rawdata"] = rawdata.hex()

    log["user_id"] = user_id

    if user_name:
        log["user_name"] = user_name

    notification_api.notify_subject(b"door_event", json.dumps(log))
    return ret
