from django.core.management.base import BaseCommand
from django.db import transaction
import datetime
import subprocess
import calendar
import json

from hackman_payments import models


class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **kwargs):
        p = subprocess.run([
            'git', '-C', 'dsl-accounts/', 'pull', '-f', 'origin', 'master'
        ], stdout=subprocess.PIPE)
        if not p.returncode == 0:
            raise RuntimeError(p)

        p = subprocess.run([
            './dsl-accounts/balance.py',
            '--split',
            'json_dues'], stdout=subprocess.PIPE)
        if not p.returncode == 0:
            raise RuntimeError(p)

        data = json.loads(p.stdout)

        tags = models.PaymentTag.objects.all()
        tags = tags.filter(tag__in=data.keys())
        tags = tags.prefetch_related('user')

        for t in tags:
            for paid_period in data[t.tag].keys():
                year, month = map(int, paid_period.split('-'))
                valid_until = datetime.date(
                    year,
                    month,
                    calendar.monthrange(year, month)[1])

                payment, created = models.Payment.objects.get_or_create(
                    user=t.user,
                    valid_until=valid_until)
