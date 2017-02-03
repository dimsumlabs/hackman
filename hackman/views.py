from django.contrib.auth.decorators import login_required
from django.contrib.messages.api import MessageFailure
from django.contrib.messages import get_messages
from datetime import datetime, date, timedelta
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib import auth
from django import shortcuts
from django import http
import calendar

from hackman_payments import api as payment_api
from hackman_rfid import api as rfid_api

from . import forms


def _ctx_from_request(request, update_ctx=None):
    ctx = {
        'messages': get_messages(request),
        'request': request,
    }
    if update_ctx:
        ctx.update(update_ctx)
    return ctx


def _get_next_month(year, month):
    cur = date(year, month, calendar.monthrange(year, month)[1])
    return cur+timedelta(days=1)


def _get_prev_current_and_three_next_months():
    now = datetime.utcnow().date()
    prev_month = (date(now.year, now.month, 1)-timedelta(days=1))

    months = [prev_month, now]

    for _ in range(3):
        prev = months[-1]
        months.append(_get_next_month(prev.year, prev.month))

    return [
        '{year}-{month:02d}'.format(year=i.year, month=i.month)
        for i in months
    ]


def login(request):

    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(**form.cleaned_data)

            if user is not None and user.is_active:
                auth.login(request, user)
                return shortcuts.redirect('/')

            else:
                return http.HttpResponseBadRequest(
                    '<h1>Wrong username/password</h1>')

    return shortcuts.render(
        request, 'login.jinja2', context=_ctx_from_request(
            request, {
                'login_form': forms.LoginForm(),
            }))


def account_create(request):
    if request.method != 'POST':
        return http.HttpResponseBadRequest('Request not POST')

    form = forms.LoginForm(request.POST)
    if not form.is_valid():
        return http.HttpResponseBadRequest(
            '<h1>Error</h1>')

    user = get_user_model().objects.create_user(**form.cleaned_data)
    auth.login(request, user)
    return shortcuts.redirect('/')


def logout(request):  # pragma: no cover
    auth.logout(request)
    return shortcuts.redirect('/login/')


@login_required(login_url='/login/')
def index(request):  # pragma: no cover

    return shortcuts.render(
        request, 'index.jinja2',
        context=_ctx_from_request(request, update_ctx={
            'payment_form': forms.PaymentForm(
                year_month_choices=_get_prev_current_and_three_next_months())
            }))


@login_required(login_url='/login/')
def door_open(request, _door_api=None):
    from hackman import api as hackman_api

    if not hackman_api.door_open_if_paid(request.user.id, _door_api):
        return http.HttpResponseForbidden('<h1>You have not paid!</h1>')

    return shortcuts.redirect('/')


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
        year_month_choices=_get_prev_current_and_three_next_months())
    if not form.is_valid():
        return http.HttpResponseBadRequest('Form error')

    year, month = form.cleaned_data['year_month']
    payment_api.payment_submit(request.user.id, year, month,
                               form.cleaned_data['amount'])

    try:
        messages.add_message(
            request, messages.SUCCESS, 'Payment submitted')
    except MessageFailure:  # pragma: no cover
        pass

    return shortcuts.redirect('/')
