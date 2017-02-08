from django import http
import zmq

from . import screen_views as views


@views.screen_whitelist_check
def whitelisted_view(request):
    return http.HttpResponse()


def test_whitelist(rf):
    request = rf.get('/mock_url/')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    response = whitelisted_view(request)
    assert response.status_code == 200


def test_whitelist_not_whitelisted_ip(rf):
    request = rf.get('/mock_url/')
    request.META['REMOTE_ADDR'] = '127.0.0.2'
    response = whitelisted_view(request)
    assert response.status_code == 403


def test_poll_timeout(rf):
    request = rf.get('/screen/poll/')
    response = views.poll(request, _timeout=0.001)
    assert response.status_code == 304


def test_poll(rf):
    messages = [
        b'DOOR_OPEN',
        b'DOOR_OPEN_GRACE',
        b'DOOR_OPEN_DENIED',
        b'CARD_UNPAIRED',
    ]

    ctx = zmq.Context()
    srv_sock = ctx.socket(zmq.PUB)
    sock = ctx.socket(zmq.SUB)
    for msg in messages:
        sock.setsockopt(zmq.SUBSCRIBE, msg)
    srv_sock.bind('inproc://hackman_test_poll')
    sock.connect('inproc://hackman_test_poll')
    for msg in messages:
        srv_sock.send(msg)

    responses = []
    request = rf.get('/screen/poll/')
    for _ in messages:
        responses.append(
            views.poll(request,
                       _sock=sock,
                       _timeout=0.01))

    assert responses[0].status_code == 302
    assert responses[0].url == '/screen/welcome/'

    assert responses[1].status_code == 302
    assert responses[1].url == '/screen/remind_payment/'

    assert responses[2].status_code == 302
    assert responses[2].url == '/screen/unpaid_membership/'

    assert responses[3].status_code == 302
    assert responses[3].url == '/screen/unpaired_card/'
