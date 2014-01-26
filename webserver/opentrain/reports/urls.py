from django.conf.urls import patterns, url, include

import views

urlpatterns = patterns('',
    url(r'add/$',views.add),
    url(r'get/$',views.show),
)






