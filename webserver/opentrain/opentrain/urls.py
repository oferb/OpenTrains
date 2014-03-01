from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
admin.autodiscover()

from tastypie.api import Api
import analysis.api 

tp = Api(api_name='v1')

analysis.api.register_all(tp)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'opentrain.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$',RedirectView.as_view(url='/gtfs/search-in/')),
    url(r'^gtfs/',include('gtfs.urls',namespace='gtfs')),
    url(r'^reports/',include('reports.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^analysis/',include('analysis.urls',namespace='analysis')),
    url(r'^api/1/',include('ot_api.urls',namespace='ot_api')),
    url(r'^api2/', include(tp.urls)),
    url(r'^static/jsi18n/he/django.js$', 'gtfs.views.home'),
)

