import json
import common.ot_utils
import datetime
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.conf import settings
import urllib

def _prepare_list_resp(req,items,info=None):
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
        

def get_trip_ids_for_date(request,*args,**kwargs):
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
    
def get_trip_details(request,trip_id):
    from gtfs.models import Trip
    trip = Trip.objects.get(trip_id=trip_id)
    result = trip.to_json_full()
    return HttpResponse(status=200,content=json.dumps(result),content_type='application/json')

def get_current_trips(req):
    import analysis.logic
    current_trips = analysis.logic.get_current_trips()    
    return _prepare_list_resp(req, current_trips)

def get_trips_location(req):
    import analysis.logic
    trip_ids = req.GET.get('trip_ids',None)
    if not trip_ids:
        return HttpResponseBadRequest('Must specify trip_ids')
    live_trips = analysis.logic.get_trips_location(trip_ids.split(','))     
    result = dict(objects=live_trips)
    result['meta'] = dict(is_fake=settings.FAKE_CUR)
    return HttpResponse(content=json.dumps(result),content_type='application/json',status=200)

def get_devices(req):
    import analysis.logic
    devices = analysis.logic.get_devices_summary()
    return _prepare_list_resp(req,devices)

def get_device_reports(req,device_id):
    import analysis.logic
    info = dict()
    info['since_id'] = int(req.GET.get('since_id',0))
    info['limit'] = int(req.GET.get('limit',200))
    info['offset'] = int(req.GET.get('offset',0))
    reports = analysis.logic.get_device_reports(device_id,info)
    return _prepare_list_resp(req,reports,info)

    
    