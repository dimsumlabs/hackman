from hackman_door import api as door_api
from unittest import mock
import zmq


def test_public_api_open_msg():
    sock = mock.Mock()
    door_api.open(_sock=sock)
    sock.send.assert_called_with(b'OPEN', flags=zmq.NOBLOCK)


def test_public_api_close_msg():
    sock = mock.Mock()
    door_api.close(_sock=sock)
    sock.send.assert_called_with(b'CLOSE', flags=zmq.NOBLOCK)
