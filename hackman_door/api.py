from hackman_notifier import api as notification_api

__all__ = ["open", "close"]


def open(_r=None):
    """Send open door command to door daemon instance"""
    notification_api.notify_subject("door_action", "OPEN", _r=_r)


def close(_r=None):
    """Send close door command to door daemon instance"""
    notification_api.notify_subject("door_action", "CLOSE", _r=_r)
