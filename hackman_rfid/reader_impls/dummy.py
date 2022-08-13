import typing
import os


def get_cards() -> typing.Generator[typing.Tuple[bytes, bytes], None, None]:
    """Dummy interface that yields random cards"""

    while True:
        random = os.urandom(10)
        yield (random, random)
