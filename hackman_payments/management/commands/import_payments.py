from django.core.management.base import BaseCommand
from hackman_payments import api as payment_api
from django_redis import get_redis_connection
import subprocess
import json
import sys

from hackman_payments import models


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        p = subprocess.run([
            'git', '-C', 'dsl-accounts/', 'pull', '-f', 'origin', 'master'
        ], stdout=subprocess.PIPE)
        if p.returncode != 0:
            sys.stderr.write('Git exited with non-zero exit code: {}\n'.format(
                p.returncode))

        p = subprocess.run([
            './dsl-accounts/balance.py',
            '--split',
            'json_payments'], stdout=subprocess.PIPE)
        if not p.returncode == 0:
            raise RuntimeError(p)

        data = json.loads(p.stdout)

        tags = models.PaymentTag.objects.all()
        tags = tags.prefetch_related('user')

        r = redis_pipe = get_redis_connection('default')
        pipe = r.pipeline()
        for t in tags:
            last_payment = data[t.make_key()]
            year, month = map(int, last_payment.split('-'))
            payment_api.payment_submit(t.user.id,
                                       year,
                                       month,
                                       _redis_pipe=redis_pipe)

        pipe.execute()
