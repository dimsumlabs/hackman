from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from django.conf import settings
from django import shortcuts
from django import http
import urllib.parse
import functools
import json

from hackman_rfid import api as rfid_api
from .lib import get_remote_ip


def screen_whitelist_check(f):
    """Check if device accessing screen endpoints are in IP whitelist"""

    @functools.wraps(f)
    def auth(request, *args, **kwargs):
        remote_ip = get_remote_ip(request)

        if remote_ip not in settings.SCREEN_VIEWS_WHITELIST:
            return http.HttpResponseForbidden(
                '<h1>Not in screen whitelist</h1>')

        return f(request, *args, **kwargs)

    return auth


@screen_whitelist_check
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


@screen_whitelist_check
def index(request):  # pragma: no cover
    return shortcuts.render(
        request, 'screen/index.jinja2')


def _user_view(request, tpl):  # pragma: no cover
    try:
        user = get_user_model().objects.get(id=request.GET.get('user_id'))
    except get_user_model().DoesNotExist:
        return shortcuts.redirect('/screen/')
    return shortcuts.render(
        request, tpl, context={
            'user': user
        })


@screen_whitelist_check
def welcome(request):  # pragma: no cover
    # Get last access and show welcome screen
    return _user_view(request, 'screen/welcome.jinja2')


@screen_whitelist_check
def remind_payment(request):  # pragma: no cover
    """Member is under grace period, say hi and remind to pay"""
    # Get last access and show payment reminder screen
    return _user_view(request, 'screen/remind_payment.jinja2')


@screen_whitelist_check
def unpaid_membership(request):  # pragma: no cover
    """Unpaid membership, shame on you"""
    return _user_view(request, 'screen/unpaid_membership.jinja2')


@screen_whitelist_check
def unpaired_card(request):  # pragma: no cover
    card = rfid_api.card_get(request.GET.get('card_id'))
    if not card:
        return shortcuts.redirect('/screen/')
    return shortcuts.render(
        request, 'screen/unpaired_card.jinja2', context={
            'card': card
        })
