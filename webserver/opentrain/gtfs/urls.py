from django.conf.urls import patterns, url, include

import views

from tastypie.api import Api
import api

v1_api = Api(api_name='v1')
api.register_all(v1_api)

urlpatterns = patterns('',
    url(r'^home/$',views.gtfs_home),
    url(r'^download/$',views.download_gtfs),
    url(r'^create-models/$',views.create_all),
    url(r'^create-superuser/$',views.create_superuser),
    url(r'^api/', include(v1_api.urls))
)

