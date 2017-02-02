import os


def get_cards():
    '''Dummy interface that yields random cards'''

    while True:
        yield os.urandom(10)
