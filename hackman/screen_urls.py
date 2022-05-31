from django.urls import path

from . import screen_views as views


urls = ([
    path(r'welcome/', views.welcome),
    path(r'remind_payment/', views.remind_payment),
    path(r'unpaid_membership/', views.unpaid_membership),
    path(r'unpaired_card/', views.unpaired_card),
    path(r'poll/', views.poll),
    path(r'', views.index),
], 'screen', 'screen')
