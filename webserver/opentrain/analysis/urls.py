from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'labels_map/$',views.labels_map,name="show-labels"), 
)
