from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import app.views

urlpatterns = patterns('',
    url(r'^$', app.views.index, name='index'),
    url(r'^dynastyffonly', app.views.dynastyffonly, name='dynastyffonly'),
    url(r'^dynastyff2qb', app.views.dynastyff2qb, name='dynastyff2qb'),
    url(r'^dynastyffmixed', app.views.dynastyffmixed, name='dynastyffmixed'),
    url(r'^dlf', app.views.dlf, name='dlf'),
    url(r'^admin/', include(admin.site.urls)),
)
