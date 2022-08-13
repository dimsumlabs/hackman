from .settings_dev import *  # noqa


AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)

DOOR_LOCK = {
    "BACKEND": "hackman_door.door.impls.dummy",
    "BIND_URI": "inproc://doord_upstream",
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:31337/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
            "SOCKET_TIMEOUT": 5,  # in seconds
        },
    }
}
