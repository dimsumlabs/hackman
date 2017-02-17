from django_redis import get_redis_connection


def notify_subject(subject, payload=None, _r=None):
    r = _r or get_redis_connection("default")
    r.publish(subject, payload or '')
