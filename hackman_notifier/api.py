from django.conf import settings  # noqa
import zmq


_zmq_ctx = zmq.Context()
_srv_sock = _zmq_ctx.socket(zmq.PUB)
_srv_sock.bind(settings.NOTIFICATIONS_BIND_URI)


def notify_subject(subject, _sock=None):
    if isinstance(subject, str):
        subject = subject.encode('utf8')

    sock = _sock or _srv_sock
    sock.send(subject, flags=zmq.NOBLOCK)
