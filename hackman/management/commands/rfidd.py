from hackman_notifier import api as notification_api
from django.core.management.base import BaseCommand

from hackman_rfid import api as rfid_api
from hackman import api as hackman_api

import json


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for card_hash in rfid_api.cards_read():

            card = rfid_api.card_validate(card_hash)
            if not card:
                continue

            if not card.user_id:
                notification_api.notify_subject(b'door_event', json.dumps({
                    'event': 'CARD_UNPAIRED',
                    'card_id': card.id
                }))
                continue

            hackman_api.door_open_if_paid(card.user_id)
