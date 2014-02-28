import json
import common.ot_utils
import datetime
from django.http.response import HttpResponse


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

