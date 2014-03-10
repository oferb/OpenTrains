from django.conf.urls import patterns, url, include

import views

urlpatterns = patterns('',
    url(r'config/?$',views.get_config),
)






