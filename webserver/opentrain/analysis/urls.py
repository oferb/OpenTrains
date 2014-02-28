from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^device-reports/$',views.show_device_reports,name="device-reports"),
    url(r'^live-trips/$',views.show_live_trains,name="live-trips"),
    url(r'^report-details/$',views.ShowReportDetails.as_view(),name='report-details'), 
)
