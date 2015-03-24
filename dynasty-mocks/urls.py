from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import app.views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', app.views.index, name='index'),
    url(r'^dynastyffonly$', app.views.dynastyffonly, name='dynastyffonly'),
    url(r'^dynastyff2qb$', app.views.dynastyff2qb, name='dynastyff2qb'),
    url(r'^nasty26$', app.views.nasty26, name='nasty26'),
    url(r'^generate_report$', app.views.generate_report, name='generate_report'),
    url(r'^dynastyffmixed$', app.views.dynastyffmixed, name='dynastyffmixed'),
    url(r'^test$', app.views.test, name='test'),
    url(r'^admin/$', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
