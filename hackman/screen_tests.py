from django import http

from . import screen_views as views


@views.screen_ip_check
def whitelisted_view(request):
    return http.HttpResponse()


def test_whitelist(rf):
    request = rf.get('/mock_url/')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    response = whitelisted_view(request)
    assert response.status_code == 200


def test_whitelist_not_whitelisted_ip(rf):
    request = rf.get('/mock_url/')
    request.META['REMOTE_ADDR'] = '8.8.8.8'
    response = whitelisted_view(request)
    assert response.status_code == 403


def test_poll_timeout(rf):
    request = rf.get('/screen/poll/')
    response = views.poll(request, _timeout=0.001)
    assert response.status_code == 200
