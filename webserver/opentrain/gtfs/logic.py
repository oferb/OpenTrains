import models

def get_stations():
    result = models.Stop.objects.all().order_by('stop_name')
    return list(result)

def get_stations_choices():
    stations = get_stations()
    result = []
    for station in stations:
        result.append((unicode(station.stop_id),station.stop_name))
    return tuple(result)


def do_search(kind,in_station=None,from_station=None,to_station=None,when=None,before=None,after=None):
    before = int(before)
    after = int(after)
    if kind == 'search-in':
        return do_search_in(in_station,when,before,after)
    elif kind == 'search-between':
        return do_seatch_between(from_station,to_station,when,before,after)
    else:
        raise Exception('Illegal kind %s' % (kind))

WEEKDAY_FIELDS = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

def do_search_in(in_station,when,before,after):
    weekday = when.weekday()
    services = models.Service.objects.filter(start_date__lte=when,end_date__gte=when)
    wd = dict()
    wd[WEEKDAY_FIELDS[weekday]] = True
    services = services.filter(**wd)
    service_ids = services.values_list('service_id')
    trip_ids_on_date = models.Trip.objects.filter(service_id__in=service_ids).values_list('trip_id')
    
    stop_times = models.StopTime.objects.filter(stop_id=in_station).filter(trip_id__in=trip_ids_on_date)
    normal_time = when.hour * 60 + when.minute
    stop_times = stop_times.filter(arrival_time__gt=normal_time-before,arrival_time__lt=normal_time+after)
    stop_times = stop_times.order_by('arrival_time')
   
   
    #trips_on_station_in_date = trips_in_station
    #route_ids = models.Trip.objects.filter(trip_id__in=trip_ids).values_list('route_id')
    #routes = models.Route.objects.filter(route_id__in=route_ids)
    
    return stop_times

def do_seatch_between(from_station,to_station,when,before,after):
    pass



