from hackman_notifier import api as notification_api
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection
import typing

from hackman_rfid import api as rfid_api
from hackman import api as hackman_api

import json


class Command(BaseCommand):
    def handle(self, *args: typing.Tuple[str], **kwargs: typing.Any) -> None:
        r = get_redis_connection("default")

        for card_hash, rawdata in rfid_api.cards_read():

            card = rfid_api.card_validate(card_hash)
            if not card:
                continue

            if not card.user_id:  # type: ignore
                r.set("rfid_last_unpaired", card.id)
                notification_api.notify_subject(
                    b"door_event",
                    json.dumps(
                        {
                            "event": "CARD_UNPAIRED",
                            "card_id": card.id,
                            "rawdata": rawdata.hex(),
                        }
                    ),
                )
                continue

            # TODO:
            # - lookup user_name and send it to the door open

            hackman_api.door_open_if_paid(
                card.user_id,  # type: ignore
                source="CARD",
                rawdata=rawdata,
            )
