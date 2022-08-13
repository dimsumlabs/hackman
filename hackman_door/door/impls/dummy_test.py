import typing


class Door:
    def __init__(self) -> None:
        self.opened: typing.Optional[bool] = None

    def open(self, open_time: typing.Optional[float] = None) -> None:
        self.opened = True

    def close(self) -> None:
        self.opened = False
