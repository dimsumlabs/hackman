from django.core.management.base import BaseCommand
from hackman_payments import api as payment_api
from hackman_payments.models import PaymentTag
from django_redis import get_redis_connection
from urllib.request import urlopen
import json
import sys
import os

from hackman_payments import models

URL = "https://dimsumlabs.github.io/dsl-accounts-pages/payments.json"


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            res = urlopen(URL)
            text = res.read().decode()
            cache = open('payments.json.tmp', 'w')
            cache.write(text)
            cache.close()
            os.rename('payments.json.tmp', 'payments.json')
        except Exception as e:  # noqa - go jump in a lake pyflakes
            sys.stderr.write(repr(e))

            # any error at all, we try to fall back to the cached data
            cache = open('payments.json', 'r')
            text = cache.read()

        data = json.loads(text)

        import_tags = set(
            k for k in data.keys()
            if k.split(':', 1)[0] == 'dues')
        db_tags = set(t.make_key() for t in PaymentTag.objects.all())

        tags = models.PaymentTag.objects.all()
        tags = tags.prefetch_related('user')

        r = redis_pipe = get_redis_connection('default')
        pipe = r.pipeline()
        for t in tags:
            try:
                last_payment = data[t.make_key()]
            except KeyError:
                continue

            year, month = map(int, last_payment.split('-'))
            if not t.user_id:
                continue

            payment_api.payment_submit(
                t.user.id,
                year,
                month,
                _redis_pipe=redis_pipe)

        pipe.execute()

        for missed_tag in (import_tags-db_tags):
            hashtag, tag = missed_tag.split(':', 1)
            PaymentTag.objects.create(
                hashtag=hashtag,
                tag=tag)
