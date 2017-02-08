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
from django.conf.urls import url
from django.contrib import admin

from . import views
from . import screen_urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^screen/', screen_urls.urls),
    url(r'^login/', views.login),
    url(r'^logout/', views.logout),
    url(r'^door_open/', views.door_open),
    url(r'^rfid_pair/', views.rfid_pair),
    url(r'^account_create/', views.account_create),
    url(r'^payment_submit/', views.payment_submit),
    url(r'^$', views.index),
]
