from django.conf import settings
import zmq

__all__ = ['open', 'close']


_zmq_ctx = zmq.Context()
_client_sock = _zmq_ctx.socket(zmq.PUB)
_client_sock.connect(settings.DOOR_LOCK['BIND_URI'])


def open(_sock=None):
    """Send open door command to door daemon instance"""
    sock = _sock or _client_sock
    sock.send(b'OPEN', flags=zmq.NOBLOCK)


def close(_sock=None):
    """Send close door command to door daemon instance"""
    sock = _sock or _client_sock
    sock.send(b'CLOSE', flags=zmq.NOBLOCK)
