from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from django import shortcuts
from django.http import HttpRequest, HttpResponse
from django import http
import urllib.parse
from IPy import IP
import functools
import typing
import json

from hackman_rfid import api as rfid_api
from .lib import get_remote_ip


def screen_ip_check(f) -> typing.Callable:  # type: ignore
    """Check if device accessing screen endpoints are in IP whitelist"""

    @functools.wraps(f)
    def auth(
        request: HttpRequest, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Any:
        ip_type = IP(get_remote_ip(request)).iptype()
        if ip_type != "PRIVATE" and ip_type != "LOOPBACK":
            return http.HttpResponseForbidden(
                "Screen views can only be accessed on lan"
            )

        return f(request, *args, **kwargs)

    return auth


@screen_ip_check
def poll(
    request: HttpRequest, _timeout: float = 60
) -> HttpResponse:  # pragma: no cover
    """Long polling view that redirects screen to correct view"""

    redirects = {
        "DOOR_OPEN": "/screen/welcome/",
        "DOOR_OPEN_GRACE": "/screen/remind_payment/",
        "DOOR_OPEN_DENIED": "/screen/unpaid_membership/",
        "CARD_UNPAIRED": "/screen/unpaired_card/",
    }

    r = get_redis_connection("default")
    ps = r.pubsub()
    try:
        ps.subscribe("door_event")

        msg = None
        while not msg:
            m = ps.get_message(timeout=_timeout)

            if not m:
                return http.HttpResponse()

            if m["type"] == "message":
                msg = m

        msg = json.loads(msg["data"])

        url = redirects[msg.pop("event")]
        url = "?".join((url, urllib.parse.urlencode(msg)))
        return http.HttpResponse(url)

    finally:
        ps.unsubscribe()


@screen_ip_check
def index(request: HttpRequest) -> HttpResponse:
    return shortcuts.render(request, "screen/index.jinja2")


def _user_view(request: HttpRequest, tpl: typing.Any) -> HttpResponse:
    try:
        user = get_user_model().objects.get(id=request.GET.get("user_id"))
    except get_user_model().DoesNotExist:
        return shortcuts.redirect("/screen/")
    return shortcuts.render(request, tpl, context={"user": user})


@screen_ip_check
def welcome(request: HttpRequest) -> HttpResponse:
    # Get last access and show welcome screen
    return _user_view(request, "screen/welcome.jinja2")


@screen_ip_check
def remind_payment(request: HttpRequest) -> HttpResponse:
    """Member is under grace period, say hi and remind to pay"""
    # Get last access and show payment reminder screen
    return _user_view(request, "screen/remind_payment.jinja2")


@screen_ip_check
def unpaid_membership(request: HttpRequest) -> HttpResponse:
    """Unpaid membership, shame on you"""
    return _user_view(request, "screen/unpaid_membership.jinja2")


@screen_ip_check
def unpaired_card(request: HttpRequest) -> HttpResponse:
    card = rfid_api.card_get(int(request.GET["card_id"]))
    if not card:
        return shortcuts.redirect("/screen/")
    return shortcuts.render(
        request, "screen/unpaired_card.jinja2", context={"card": card}
    )
