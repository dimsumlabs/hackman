"""hackman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.conf.urls import url, include
from django.http import HttpResponse
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static

from . import views
from . import rest_api
from . import screen_urls


def robots(request):
    return HttpResponse('User-agent: *\nDisallow: /',
                        content_type='text/plain')


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^screen/', screen_urls.urls),
    url(r'^robots.txt$', robots),
    url(r'^login/', views.login, name='login'),
    url(r'^logout/', views.logout),

    url('^password_change/$', auth_views.password_change,
        name='password_change'),
    url('^password_change/done/$', views.password_change_done,
        name='password_change_done'),
    url('^password_reset/$', auth_views.password_reset, name='password_reset'),
    url('^password_reset/done/$', auth_views.password_reset_done,
        name='password_reset_done'),
    url('^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',  # noqa
        auth_views.password_reset_confirm,
        name='password_reset_confirm'),
    url('^reset/done/$', auth_views.password_reset_complete,
        name='password_reset_complete'),

    url(r'^door_open/', views.door_open),
    url(r'^rfid_pair/', views.rfid_pair),
    url(r'^account_create/', views.account_create, name='account_create'),
    url(r'^payment_submit/', views.payment_submit),
    url(r'^$', views.index),
    url(r'^oauth/', include('oauth2_provider.urls',
                            namespace='oauth2_provider')),

    url(r'^api/v1/profile/', rest_api.profile),
    url(r'^api/v1/tags_not_matching/', rest_api.tags_not_matching),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
