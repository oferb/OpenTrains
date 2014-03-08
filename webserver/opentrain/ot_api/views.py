import json
import common.ot_utils
import datetime
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.conf import settings
import urllib

from django.views.generic import View
from django.shortcuts import render

def show_docs(request):
    ctx = dict()
    ctx['apis'] = ApiView.get_api_insts()
    
    return render(request,'ot_api/docs.html',ctx)

class ApiView(View):
    def _prepare_list_resp(self,req,items,info=None):
        info = info or dict()
        count = len(items)
        total_count = info.get('total_count',len(items))
        meta=dict(count=count,total_count=total_count)
        if total_count > count:
            if total_count > info['offset'] + info['limit']:
                d = req.GET.dict()
                d['offset'] = info['offset'] + info['limit']
                meta['next'] = req.path + '?' + urllib.urlencode(d)
        meta['is_fake'] = settings.FAKE_CUR
        content = dict(objects=items,meta=meta)
        return HttpResponse(content=json.dumps(content),content_type='application/json',status=200)
    
    def get_doc(self):
        return self.__doc__
    
    def get_api_url_nice(self):
        u = self.api_url
        u =  u.replace('$','').replace('^','')
        u = '/api/1/' + u
        return u
    
    @classmethod
    def get_api_insts(cls):
        return [c() for c in cls.get_api_classes()]
    
    @classmethod
    def get_api_classes(cls):
        return cls.__subclasses__()
    
    
    @classmethod
    def get_urls(cls):
        from django.conf.urls import url
        urls = []
        for ac in cls.get_api_classes():
            urls.append(url(ac.api_url,ac.as_view()))
        return urls
    
class TripIdsForDate(ApiView):
    """ Return list of trips for given date """
    api_url = r'^trips/trips-for-date/$'
    def get(self,request):
        import gtfs.logic
        date = request.GET.get('date')
        today = bool(int(request.GET.get('today','0')))
        if not today and not date:
            raise Exception('Must have either today or date')
        if today:
            dt = common.ot_utils.get_localtime_now().date()
        else:
            day,month,year = date.split('/')
            dt = datetime.date(year=int(year),month=int(month),day=int(day))
        trips = gtfs.logic.get_all_trips_in_date(dt)
        objects=[trip.trip_id for trip in trips]
        result = dict(objects=objects,
                      meta=dict(total_count=len(objects)))
        return HttpResponse(status=200,content=json.dumps(result),content_type='application/json')

class TripDetails(ApiView):
    """ Return details for trip with trip_id trip_id"""
    api_url = r'^trips/(?P<trip_id>\w+)/details/$'
    def get(self,request,trip_id):
        from gtfs.models import Trip
        trip = Trip.objects.get(trip_id=trip_id)
        result = trip.to_json_full()
        return HttpResponse(status=200,content=json.dumps(result),content_type='application/json')

class CurrentTrips(ApiView):
    """ Return current trips """
    api_url = r'^trips/current/$'
    def get(self,request):
        import analysis.logic
        current_trips = analysis.logic.get_current_trips()    
        return self._prepare_list_resp(request, current_trips)

class TripsLocation(ApiView):
    """ Return location (exp and cur) of trips given in comma separated GET paramter trip_ids """
    api_url = r'^trips/cur-location/$'
    def get(self,request):
        import analysis.logic
        trip_ids = request.GET.get('trip_ids',None)
        if not trip_ids:
            return HttpResponseBadRequest('Must specify trip_ids')
        live_trips = analysis.logic.get_trips_location(trip_ids.split(','))     
        result = dict(objects=live_trips)
        result['meta'] = dict(is_fake=settings.FAKE_CUR)
        return HttpResponse(content=json.dumps(result),content_type='application/json',status=200)

class Devices(ApiView): 
    """ Return list of devices """
    api_url = r'^devices/$'
    def get(self,request):
        import analysis.logic
        devices = analysis.logic.get_devices_summary()
        return self._prepare_list_resp(request,devices)

class DeviceReports(ApiView):
    """ Return reports for given device with id device_id"""
    api_url = r'^devices/(?P<device_id>\w+)/reports/'
    def get(self,request,device_id):
        import analysis.logic
        info = dict()
        info['since_id'] = int(request.GET.get('since_id',0))
        info['limit'] = int(request.GET.get('limit',200))
        info['offset'] = int(request.GET.get('offset',0))
        reports = analysis.logic.get_device_reports(device_id,info)
        return self._prepare_list_resp(request,reports,info)

    