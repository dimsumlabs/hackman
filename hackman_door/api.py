from hackman_notifier import api as notification_api
import typing

__all__ = ["open", "close"]


def open(_r: typing.Any = None) -> None:
    """Send open door command to door daemon instance"""
    notification_api.notify_subject("door_action", "OPEN", _r=_r)


def close(_r: typing.Any = None) -> None:
    """Send close door command to door daemon instance"""
    notification_api.notify_subject("door_action", "CLOSE", _r=_r)
