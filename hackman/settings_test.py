from .settings_dev import *  # noqa


DOOR_LOCK = {
    'BACKEND': 'hackman_door.door.impls.dummy',
    'BIND_URI': 'inproc://doord_upstream',
}


NOTIFICATIONS_BIND_URI = 'inproc://notifications'
