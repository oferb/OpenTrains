from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^home/$',views.GtfsSearchBetween.as_view(),name='home'),
    url(r'^search-between/$',views.GtfsSearchBetween.as_view(),name='search-between'), 
    url(r'^search-in/$',views.GtfsSearchIn.as_view(),name='search-in'),   
    url(r'^download/$',views.download_gtfs),
    url(r'^maps/(?P<trip_id>\w+)/',views.show_map,name='show-map'), 
    url(r'^create-models/$',views.create_all),
    url(r'^create-superuser/$',views.create_superuser),
)



