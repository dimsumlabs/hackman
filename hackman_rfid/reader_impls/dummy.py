import os


def get_cards():
    '''Dummy interface that yields random cards'''

    while True:
        random = os.urandom(10)
        yield (random, random)
