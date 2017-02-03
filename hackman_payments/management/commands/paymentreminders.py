from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.conf import settings

from hackman_payments import api as payment_api


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        emails = list(get_user_model().objects.filter(
            id__in=payment_api.unpaid_users()).values_list('email', flat=True))

        email_body = payment_api.payment_reminder_email_format()

        msg = EmailMultiAlternatives(
            'Dimsumlabs payment reminder',  # Subject
            email_body,
            settings.EMAILS_FROM,
            [],  # Empty to
            bcc=emails)
        msg.send()
