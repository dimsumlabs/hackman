from .settings_dev import *  # noqa


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

DOOR_LOCK = {
    'BACKEND': 'hackman_door.door.impls.dummy',
    'BIND_URI': 'inproc://doord_upstream',
}
