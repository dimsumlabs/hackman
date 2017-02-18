from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

from hackman_door.door import Door


class Command(BaseCommand):

    help = 'Run door opening daemon'

    def handle(self, *args, **options):
        r = get_redis_connection()
        ps = r.pubsub()
        ps.subscribe('door_action')

        door = Door()

        while True:
            msg = ps.get_message(timeout=10)
            if not msg or msg['type'] != 'message':
                continue

            action = msg['data']
            if action == b'OPEN':
                door.open()

            elif action == b'CLOSE':
                door.close()

            else:  # pragma: no cover
                # This should never happen but might happen from some
                # future coding mistake where subscription is created
                # but not handled
                raise RuntimeError('Incorrect code, fix that shit')
