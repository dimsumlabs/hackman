from django.core.management.base import BaseCommand
from django.conf import settings
import zmq

from hackman_door.door import Door


class Command(BaseCommand):

    help = 'Run door opening daemon'

    def handle(self, *args, **options):
        print("TODO: Move away logic from here into libs (more testable)")

        ctx = zmq.Context()
        subscriber = ctx.socket(zmq.SUB)
        subscriber.setsockopt(zmq.SUBSCRIBE, b'OPEN')
        subscriber.setsockopt(zmq.SUBSCRIBE, b'CLOSE')
        subscriber.bind(settings.DOOR_LOCK['BIND_URI'])

        door = Door()

        while True:
            msg = subscriber.recv()

            if msg == b'OPEN':
                door.open()

            elif msg == b'CLOSE':
                door.close()

            else:  # pragma: no cover
                # This should never happen but might happen from some
                # future coding mistake where subscription is created
                # but not handled
                raise RuntimeError('Incorrect code, fix that shit')
