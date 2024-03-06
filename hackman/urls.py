"""hackman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path(r'', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path(r'', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  path(r'blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.http import (
    HttpResponse,
    HttpRequest,
)
from django.contrib import admin

from django.conf import settings
from django.conf.urls.static import static

from . import views
from . import screen_urls


def robots(request: HttpRequest) -> HttpResponse:
    return HttpResponse("User-agent: *\nDisallow: /", content_type="text/plain")


urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"screen/", screen_urls.urls),
    path(r"robots.txt", robots),
    path(r"login/", views.login, name="login"),
    path(r"logout/", views.logout),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    re_path(
        "reset/(?P<uidb64>[0-9A-Za-z_-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path(r"door_open/", views.door_open),
    path(r"rfid_pair/", views.rfid_pair),
    path(r"account_actions/", views.account_actions, name="account_actions"),
    path(r"account_create/", views.account_create, name="account_create"),
    path(r"payment_submit/", views.payment_submit),
    path(r"", views.index, name="index"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
