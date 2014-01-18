from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'show-labels/$',views.show_labels,name="show-labels"), 
    url(r'select-device-reports/$',views.ShowDeviceReports.as_view(),name="select-device-reports"),
    url(r'report-details/$',views.ShowReportDetails.as_view(),name='report-details') 
)
