from django.core.management.base import BaseCommand

from hackman_rfid import api as rfid_api
from hackman import api as hackman_api


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for card_hash in rfid_api.cards_read():

            user = rfid_api.card_validate(card_hash)
            if not user:
                continue

            hackman_api.door_open_if_paid(user.id)
