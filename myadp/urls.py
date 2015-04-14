from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import app.views

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', app.views.index, name='index'),
    url(r'^contact$', app.views.contact, name='contact'),
    url(r'^custom$', app.views.custom_page, name='custom_page'),
    url(r'^generate$', app.views.generate_report, name='generate_report'),
    url(r'^report/custom$', app.views.custom_report, name='custom_report'),
    url(r'^report/dynastyffonly$', app.views.dynastyffonly, name='dynastyffonly'),
    url(r'^report/dynastyff2qb$', app.views.dynastyff2qb, name='dynastyff2qb'),
    url(r'^report/nasty26$', app.views.nasty26, name='nasty26'),
    url(r'^admin/$', include(admin.site.urls)),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
