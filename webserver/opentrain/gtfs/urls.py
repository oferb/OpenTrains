from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^create_all/',views.create_all),
)

