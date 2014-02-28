from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^trips/trips-for-date/$',views.get_trip_ids_for_date),
    url(r'^trips/(?P<trip_id>\w+)/$',views.get_trip_details), 
)



