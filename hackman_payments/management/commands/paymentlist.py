from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from hackman_payments import api as payment_api


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        print(','.join(['id', 'username', 'valid_until']))

        for user in get_user_model().objects.all():
            print("{},{},{}".format(
                str(user.id),
                user.username,
                payment_api.get_valid_until(user.id)
            ))
