from django.contrib.auth.decorators import login_required
from django.contrib.messages.api import MessageFailure
from django.contrib.messages import get_messages
from datetime import datetime, date, timedelta
from django.contrib.auth import get_user_model
from django_redis import get_redis_connection
from django.utils.http import is_safe_url
from django.contrib import messages
from calendar import monthrange
from django.contrib import auth
from django import shortcuts
from django import http
from IPy import IP

from hackman_payments import api as payment_api
from hackman_rfid import api as rfid_api


from .lib import get_remote_ip
from . import forms


# Hack to avoid using the old python3-django-ratelimit in debian
import ratelimit
if ratelimit.__version__ < '1.0.1':
    def ratelimit(**kwargs):
        def decorator(fn):
            def _wrapped(*args, **kwargs):
                return fn(*args, **kwargs)
            return _wrapped
        return decorator
else:
    from ratelimit.decorators import ratelimit


def _ctx_from_request(request, update_ctx=None):
    ctx = {
        'messages': get_messages(request),
        'request': request,
    }
    if update_ctx:
        ctx.update(update_ctx)
    return ctx


def _get_month_choices():
    now = datetime.utcnow().date()
    months = (
        (date(now.year, now.month, 1)-timedelta(days=1)),
        now,
        date(now.year, now.month, monthrange(now.year,
                                             now.month)[1]) + timedelta(days=1)
    )

    return [
        '{year}-{month:02d}'.format(year=i.year, month=i.month)
        for i in months
    ]


def password_change_done(request):  # pragma: no cover
    try:
        messages.add_message(
            request, messages.SUCCESS, 'Password changed!')
    except MessageFailure:
        pass
    return shortcuts.redirect('/')


@ratelimit(key='ip', rate='5/m')
def login(request):

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(**form.cleaned_data)

            if user is not None and user.is_active:
                auth.login(request, user)

                redir_url = form.cleaned_data['redir_url']
                if redir_url and is_safe_url(redir_url):  # pragma: no cover
                    return shortcuts.redirect(redir_url)
                else:
                    return shortcuts.redirect('/')

            else:
                result = shortcuts.render(
                    request, 'login_bad.jinja2',
                    context=_ctx_from_request(request)
                )
                result.status_code = 400
                return result

    redir_url = request.GET.get('next')
    if not is_safe_url(redir_url):
        redir_url = '/'
    return shortcuts.render(
        request, 'login.jinja2', context=_ctx_from_request(
            request, {
                'login_form': forms.LoginForm(initial={
                    'redir_url': redir_url}),
                'signup_form': forms.SignupForm(initial={
                    'redir_url': redir_url}),
            }))


def account_create(request):
    if IP(get_remote_ip(request)).iptype() != 'PRIVATE':
        return http.HttpResponseForbidden(
            'You can only register an account from within DSL')

    if request.method != 'POST':
        redir_url = request.GET.get('next')
        if not is_safe_url(redir_url):
            redir_url = '/'
        return shortcuts.render(
            request, 'account_create.jinja2', context=_ctx_from_request(
                request, {
                    'signup_form': forms.SignupForm(initial={
                        'redir_url': redir_url}),
                }))

    form = forms.SignupForm(request.POST)
    if not form.is_valid():
        return http.HttpResponseBadRequest(
            '<h1>Error</h1>')

    form_data = form.cleaned_data
    if not form_data['username']:
        form_data['username'] = form_data['email']

    redir_url = form.cleaned_data.pop('redir_url')
    user = get_user_model().objects.create_user(**form.cleaned_data)
    auth.login(request, user,
               backend='django.contrib.auth.backends.ModelBackend')

    if redir_url and is_safe_url(redir_url):  # pragma: no cover
        return shortcuts.redirect(redir_url)
    else:
        return shortcuts.redirect('/')


def logout(request):  # pragma: no cover
    auth.logout(request)
    return shortcuts.redirect('/login/')


@login_required(login_url='/login/')
def index(request):  # pragma: no cover
    r = get_redis_connection('default')
    return shortcuts.render(
        request, 'index.jinja2',
        context=_ctx_from_request(request, update_ctx={
            'payment_form': forms.PaymentForm(
                year_month_choices=_get_month_choices()),
            'rfid_pair_form': forms.RfidCardPairForm(
                initial={
                    'card_id': r.get('rfid_last_unpaired')
                })
        }))


@login_required(login_url='/login/')
def door_open(request, _door_api=None):
    from hackman import api as hackman_api

    if not hackman_api.door_open_if_paid(request.user.id, _door_api):
        result = shortcuts.render(
            request, 'unpaid.jinja2',
            context=_ctx_from_request(request)
        )
        result.status_code = 403
        return result

    try:
        messages.add_message(
            request, messages.SUCCESS, 'Opened door!')
    except MessageFailure:  # pragma: no cover
        pass

    return shortcuts.redirect('/')


@login_required(login_url='/login/')
def account_actions(request):
    r = get_redis_connection('default')
    return shortcuts.render(
        request, 'account_actions.jinja2',
        context=_ctx_from_request(request, update_ctx={
            'payment_form': forms.PaymentForm(
                year_month_choices=_get_month_choices()),
            'rfid_pair_form': forms.RfidCardPairForm(
                initial={
                    'card_id': r.get('rfid_last_unpaired')
                })
        }))


@login_required(login_url='/login/')
def rfid_pair(request):
    if request.method != 'POST':
        return http.HttpResponseBadRequest('Request not POST')

    form = forms.RfidCardPairForm(request.POST)
    if not form.is_valid():
        return http.HttpResponseBadRequest('Form error')

    try:
        rfid_api.card_pair(request.user.id, form.cleaned_data['card_id'])
    except ValueError:
        return http.HttpResponseBadRequest('Card already paired')

    try:
        messages.add_message(
            request, messages.SUCCESS, 'Paired card!')
    except MessageFailure:  # pragma: no cover
        pass

    return shortcuts.redirect('/')


@login_required(login_url='/login/')
def payment_submit(request, r=False):
    if request.method != 'POST':
        return http.HttpResponseBadRequest('Request not POST')

    form = forms.PaymentForm(
        request.POST,
        year_month_choices=_get_month_choices())
    if not form.is_valid():
        return http.HttpResponseBadRequest('Form error')

    year, month = form.cleaned_data['year_month']
    payment_api.payment_submit(request.user.id, year, month)

    try:
        messages.add_message(
            request, messages.SUCCESS, 'Payment submitted')
    except MessageFailure:  # pragma: no cover
        pass

    return shortcuts.redirect('/')
