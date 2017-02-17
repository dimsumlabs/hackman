from hackman_notifier import api as notification_api
from hackman_payments import enums as payment_enums
from hackman_payments import api as payment_api
from hackman_door import api as door_api
import json


def door_open_if_paid(user_id, _door_api=None):
    """Open door if paid and send pubsub notification accordingly"""
    paid = payment_api.has_paid(user_id)
    paid = payment_enums.PaymentGrade(paid).name

    if paid == 'PAID':
        (_door_api or door_api).open()
        notify_event = 'DOOR_OPEN'
        ret = True

    elif paid == 'GRACE':
        (_door_api or door_api).open()
        ret = True
        notify_event = 'DOOR_OPEN_GRACE'

    else:
        ret = False
        notify_event = 'DOOR_OPEN_DENIED'

    notification_api.notify_subject(b'door_event', json.dumps({
        'event': notify_event,
        'user_id': user_id
    }))
    return ret
