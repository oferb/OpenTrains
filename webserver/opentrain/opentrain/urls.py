from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from tastypie.api import Api
import gtfs.api
import reports.api

tp = Api(api_name='v1')

gtfs.api.register_all(tp)
reports.api.register_all(tp)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'opentrain.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$','gtfs.views.home'),
    url(r'^gtfs/',include('gtfs.urls')),
    url(r'^reports/',include('reports.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(tp.urls))
)


