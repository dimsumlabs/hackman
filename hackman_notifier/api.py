from django_redis import get_redis_connection
import typing


def notify_subject(
    subject: typing.Union[bytes, str],
    payload: typing.Optional[typing.Any] = None,
    _r: typing.Any = None,
) -> None:
    r = _r or get_redis_connection("default")
    r.publish(subject, payload or "")
