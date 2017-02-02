from unittest import mock
import zmq

from . import api as notification_api


def test_notify_subject_str():
    m = mock.Mock()
    notification_api.notify_subject('helloworld', _sock=m)
    m.send.assert_called_with(b'helloworld', flags=zmq.NOBLOCK)
    pass


def test_notify_subject():
    m = mock.Mock()
    notification_api.notify_subject('helloworld', _sock=m)
    m.send.assert_called_with(b'helloworld', flags=zmq.NOBLOCK)
