from django.conf.urls import patterns, url, include

import views

urlpatterns = patterns('',
    url(r'^home/$',views.gtfs_home),
    url(r'^download/$',views.download_gtfs),
    url(r'^create-models/$',views.create_all),
    url(r'^create-superuser/$',views.create_superuser),
)

