from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^download/$',views.download_gtfs),
    url(r'^create-models/$',views.create_all),
    url(r'^create-superuser/$',views.create_superuser),
)

