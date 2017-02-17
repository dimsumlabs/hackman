from .settings_dev import *  # noqa


DOOR_LOCK = {
    'BACKEND': 'hackman_door.door.impls.dummy',
    'BIND_URI': 'inproc://doord_upstream',
}


REDIS = None
