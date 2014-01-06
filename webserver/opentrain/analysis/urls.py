from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'show-labels/$',views.show_labels,name="show-labels"), 
    url(r'show-reports/$',views.show_reports,name="show-reports")
)
