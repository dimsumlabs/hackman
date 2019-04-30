from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from django import shortcuts
from django import http
import urllib.parse
from IPy import IP
import functools
import json

from hackman_rfid import api as rfid_api
from .lib import get_remote_ip


def screen_ip_check(f):
    """Check if device accessing screen endpoints are in IP whitelist"""

    @functools.wraps(f)
    def auth(request, *args, **kwargs):
        if IP(get_remote_ip(request)).iptype() != 'PRIVATE':
            return http.HttpResponseForbidden(
                'Screen views can only be accessed on lan')

        return f(request, *args, **kwargs)

    return auth


@screen_ip_check
def poll(request, _timeout=60):  # pragma: no cover
    """Long polling view that redirects screen to correct view"""

    redirects = {
        'DOOR_OPEN': '/screen/welcome/',
        'DOOR_OPEN_GRACE': '/screen/remind_payment/',
        'DOOR_OPEN_DENIED': '/screen/unpaid_membership/',
        'CARD_UNPAIRED': '/screen/unpaired_card/',
    }

    r = get_redis_connection("default")
    ps = r.pubsub()
    try:
        ps.subscribe('door_event')

        msg = None
        while not msg:
            m = ps.get_message(
                timeout=_timeout)

            if not m:
                return http.HttpResponse()

            if m['type'] == 'message':
                msg = m

        msg = json.loads(msg['data'])

        url = redirects[msg.pop('event')]
        url = '?'.join((url, urllib.parse.urlencode(msg)))
        return http.HttpResponse(url)

    finally:
        ps.unsubscribe()


@screen_ip_check
def index(request):
    return shortcuts.render(
        request, 'screen/index.jinja2')


def _user_view(request, tpl):
    try:
        user = get_user_model().objects.get(id=request.GET.get('user_id'))
    except get_user_model().DoesNotExist:
        return shortcuts.redirect('/screen/')
    return shortcuts.render(
        request, tpl, context={
            'user': user
        })


@screen_ip_check
def welcome(request):
    # Get last access and show welcome screen
    return _user_view(request, 'screen/welcome.jinja2')


@screen_ip_check
def remind_payment(request):
    """Member is under grace period, say hi and remind to pay"""
    # Get last access and show payment reminder screen
    return _user_view(request, 'screen/remind_payment.jinja2')


@screen_ip_check
def unpaid_membership(request):
    """Unpaid membership, shame on you"""
    return _user_view(request, 'screen/unpaid_membership.jinja2')


@screen_ip_check
def unpaired_card(request):
    card = rfid_api.card_get(request.GET.get('card_id'))
    if not card:
        return shortcuts.redirect('/screen/')
    return shortcuts.render(
        request, 'screen/unpaired_card.jinja2', context={
            'card': card
        })
