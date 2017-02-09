from django.conf import settings
from django import shortcuts
from django import http
import functools
import zmq

from hackman_rfid import api as rfid_api


def screen_whitelist_check(f):
    """Check if device accessing screen endpoints are in IP whitelist"""

    @functools.wraps(f)
    def auth(request, *args, **kwargs):
        remote_ip = request.META.get('HTTP_X_FORWARDED_FOR',
                                     request.META.get('REMOTE_ADDR'))
        remote_ip = remote_ip.split(',')[0]

        if remote_ip not in settings.SCREEN_VIEWS_WHITELIST:
            return http.HttpResponseForbidden(
                '<h1>Not in screen whitelist</h1>')

        return f(request, *args, **kwargs)

    return auth


@screen_whitelist_check
def poll(request, _timeout=20, _sock=None):
    """Long polling view that redirects screen to correct view"""

    redirects = {
        b'DOOR_OPEN': http.HttpResponse('/screen/welcome/'),
        b'DOOR_OPEN_GRACE': http.HttpResponse('/screen/remind_payment/'),
        b'DOOR_OPEN_DENIED': http.HttpResponse('/screen/unpaid_membership/'),
        b'CARD_UNPAIRED': http.HttpResponse('/screen/unpaired_card/'),
    }

    sock = _sock or zmq.Context().socket(zmq.SUB)
    for chan in redirects.keys():
        sock.setsockopt(zmq.SUBSCRIBE, chan)

    sock.connect(settings.NOTIFICATIONS_BIND_URI)

    poller = zmq.Poller()
    poller.register(sock, zmq.POLLIN)

    s = dict(poller.poll(1000 * _timeout))
    if sock not in s:  # No event, timeout
        return http.HttpResponse()

    msg = sock.recv()

    return redirects[msg]


@screen_whitelist_check
def index(request):  # pragma: no cover
    return shortcuts.render(
        request, 'screen/index.jinja2')


@screen_whitelist_check
def welcome(request):  # pragma: no cover
    # Get last access and show welcome screen
    card = rfid_api.access_last(paired=True)
    return shortcuts.render(
        request, 'screen/welcome.jinja2', context={
            'user': card.user
        })


@screen_whitelist_check
def remind_payment(request):  # pragma: no cover
    """Member is under grace period, say hi and remind to pay"""
    # Get last access and show payment reminder screen
    card = rfid_api.access_last(paired=True)
    return shortcuts.render(
        request, 'screen/remind_payment.jinja2', context={
            'user': card.user
        })


@screen_whitelist_check
def unpaid_membership(request):  # pragma: no cover
    """Unpaid membership, shame on you"""
    card = rfid_api.access_last(paired=True)
    return shortcuts.render(
        request, 'screen/unpaid_membership.jinja2', context={
            'user': card.user
        })


@screen_whitelist_check
def unpaired_card(request):  # pragma: no cover
    card = rfid_api.access_last(paired=False)
    return shortcuts.render(
        request, 'screen/unpaired_card.jinja2', context={
            'card': card
        })
