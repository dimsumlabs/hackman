from unittest import mock

from . import api as notification_api


def test_notify_subject_str():
    m = mock.Mock()
    notification_api.notify_subject('helloworld', _r=m)
    m.publish.assert_called_with('helloworld', '')


def test_notify_subject():
    m = mock.Mock()
    notification_api.notify_subject('helloworld', _r=m)
    m.publish.assert_called_with('helloworld', '')
