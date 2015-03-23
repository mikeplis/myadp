from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import app.views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', app.views.index, name='index'),
    url(r'^dynastyffonly$', app.views.dynastyffonly, name='dynastyffonly'),
    url(r'^api/dynastyffonly$', app.views.dynastyffonly_api, name='dynastyffonly_api'),
    url(r'^dynastyff2qb$', app.views.dynastyff2qb, name='dynastyff2qb'),
    url(r'^api/dynastyff2qb$', app.views.dynastyff2qb_api, name='dynastyff2qb_api'),
    url(r'^dynastyffmixed$', app.views.dynastyffmixed, name='dynastyffmixed'),
    url(r'^dlf$', app.views.dlf, name='dlf'),
    url(r'^api/dlf$', app.views.dlf_api, name='dlf_api'),
    url(r'^nasty26$', app.views.nasty26, name='nasty26'),
    url(r'^api/nasty26$', app.views.nasty26_api, name='nasty26_api'),
    # url(r'^dynastyffrookie$', app.views.dynastyff_rookie, name='dynastyff_rookie'),
    # url(r'^api/dynastyffrookie$', app.views.dynastyff_rookie_api, name='dynastyff_rookie_api'),
    url(r'^test$', app.views.test, name='test'),
    url(r'^test2$', app.views.test2, name='test2'),
    url(r'^admin/$', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
