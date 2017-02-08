from django.conf.urls import url

from . import screen_views as views


urls = ([
    url(r'^welcome/', views.welcome),
    url(r'^remind_payment/', views.remind_payment),
    url(r'^unpaid_membership/', views.unpaid_membership),
    url(r'^unpaired_card/', views.unpaired_card),
    url(r'^poll/', views.poll),
    url(r'^$', views.index),
], 'screen', 'screen')
