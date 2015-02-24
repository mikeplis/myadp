from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

import hello.views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'gettingstarted.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', hello.views.index, name='index'),
    url(r'^dynastyffonly', hello.views.dynastyffonly, name='dynastyffonly'),
    url(r'^dynastyffmixed', hello.views.dynastyffmixed, name='dynastyffmixed'),
    url(r'^dynastyff2qb', hello.views.dynastyff2qb, name='dynastyff2qb'),
    url(r'^db', hello.views.db, name='db'),
    url(r'^admin/', include(admin.site.urls)),

)
