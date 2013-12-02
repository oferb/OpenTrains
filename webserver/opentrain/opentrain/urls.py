from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'opentrain.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^','gtfs.views.home'),
    url(r'^gtfs/',include('gtfs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
