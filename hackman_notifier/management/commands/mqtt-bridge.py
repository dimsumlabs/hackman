from django.core.management.base import BaseCommand
from django_redis import get_redis_connection
from django.conf import settings
import paho.mqtt.client as mqtt
import json


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        r = get_redis_connection('default')
        rps = r.pubsub()

        client = mqtt.Client()
        client.connect(*settings.MQTT_CONNECT)
        client.loop_start()

        try:
            rps.subscribe('door_event')

            while True:
                m = rps.get_message(ignore_subscribe_messages=True, timeout=1)

                if not m or m['type'] != 'message':
                    continue

                client.publish('door_event',
                               json.loads(m['data'])['event'])

        finally:
            client.loop_stop()
            client.disconnect()
            rps.unsubscribe()
