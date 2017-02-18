from hackman_door import api as door_api
from unittest import mock


def test_public_api_open_msg():
    m = mock.Mock()
    door_api.open(_r=m)
    m.publish.assert_called_with('door_action', 'OPEN')


def test_public_api_close_msg():
    m = mock.Mock()
    door_api.close(_r=m)
    m.publish.assert_called_with('door_action', 'CLOSE')
