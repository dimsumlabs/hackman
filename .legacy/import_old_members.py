# DO NOT CHECK IN TO GIT
from hackman_rfid.models import RFIDCard
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.core import validators
from collections import namedtuple
from django.db import transaction
from datetime import datetime
import sqlite3
import pytz


def pass_parser(v):
    return v


def dt_parser(v):
    return pytz.timezone("Asia/Hong_Kong").localize(
        datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
    )


_fields = (
    ("id", pass_parser),
    ("email", pass_parser),
    ("salt", pass_parser),
    ("password", pass_parser),
    ("since", dt_parser),
    ("name", pass_parser),
    ("rfid", pass_parser),
)


Member = namedtuple("Member", [f[0] for f in _fields])
_parsers = [f[1] for f in _fields]

User = get_user_model()


def _get_members():
    conn = sqlite3.connect("members.db")
    r = conn.execute("SELECT {} FROM Users".format(",".join(Member._fields)))

    for m in r:
        yield Member(*(p(m) for m, p in zip(m, _parsers)))


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **kwargs):

        em_valid = validators.EmailValidator()

        for m in _get_members():

            # Skip accounts with broken email address
            try:
                em_valid(m.email)
            except ValidationError:
                continue

            first_name = ""
            last_name = ""

            if m.name:
                try:
                    first_name, last_name = m.name.split(" ")
                except ValueError:
                    first_name = m.name.strip()

            u = User.objects.create_user(
                username=m.email,
                email=m.email,
                password=m.password,
                date_joined=m.since,
                first_name=first_name,
                last_name=last_name,
            )

            if m.rfid:
                RFIDCard.objects.create(user=u, rfid_hash=m.rfid)
