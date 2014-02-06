import models
import common.ot_utils
import json

def get_stations():
    result = models.Stop.objects.all().order_by('stop_name')
    return list(result)

def get_stations_choices():
    stations = get_stations()
    result = []
    for station in stations:
        result.append((unicode(station.stop_id),station.stop_name))
    return tuple(result)

@common.ot_utils.benchit
def test1():
    from models import Trip
    trip_id = '030214_00192'
    secs = 1391451464.94
    dt = common.ot_utils.unix_time_to_localtime(secs)
    trip = Trip.objects.get(trip_id=trip_id)
    loc = get_expected_location(trip,dt)
    exp = [32.08201845, 34.79795221]
    print 'Loc = %s' % (loc)
    dist = common.ot_utils.latlon_to_meters(loc[0],loc[1],exp[0],exp[1])
    print 'Dist to expected = %f' % (dist) 
    assert loc == exp
    
@common.ot_utils.benchit
def test2():
    secs = 1391451464.94
    dt = common.ot_utils.unix_time_to_localtime(secs)
    result =  list(get_all_trips_in_datetime(dt))
    exp_trips = ['030214_00089','030214_00090','030214_00187','030214_00188','030214_00191','030214_00192','030214_00193','030214_00124','030214_00125','030214_00126','030214_00127','030214_00128','030214_00129','030214_00229','030214_00277','030214_00279','030214_00280','030214_00282','030214_00679','030214_00681','030214_00682','030214_00683','030214_00684','030214_00685','030214_00686','030214_00690','030214_00929','030214_00930','030214_00975','030214_00978','030214_00980','030214_00528','030214_00533']
    assert set(t.trip_id for t in result) == set(exp_trips)
    return result
        
        
        
def get_all_trips_in_datetime(dt):
    from models import Service,Trip
    from django.db.models import Min,Max
    local_dt = common.ot_utils.get_localtime(dt)
    normal_time = common.ot_utils.get_normal_time(dt) 
    date = local_dt.date()
    services = Service.objects.filter(start_date__gte=date,end_date__lte=date)
    service_ids = services.values_list('service_id')
    trips = Trip.objects.filter(service_id__in=service_ids)
    trips = trips.annotate(total_departure_time=Min('stoptime__departure_time'),total_arrival_time=Max('stoptime__arrival_time'))
    trips = trips.filter(total_departure_time__lte=normal_time).filter(total_arrival_time__gte=normal_time)
    trips = trips.prefetch_related('stoptime_set','stoptime_set__stop') 
    return trips

def get_all_trips_in_date(date):
    from models import Service,Trip
    services = Service.objects.filter(start_date__gte=date,end_date__lte=date)
    service_ids = services.values_list('service_id')
    return Trip.objects.filter(service_id__in=service_ids)

def get_expected_location(trip,dt):
    from models import ShapeJson
    import time
    normal_time = common.ot_utils.get_normal_time(dt)
    stop_times = list(trip.stoptime_set.all())
    stop_times.sort(key=lambda x : x.stop_sequence)
    before_stop_list = [st for st in stop_times if st.departure_time <= normal_time]
    after_stop_list = [st for st in stop_times if st.arrival_time >= normal_time]
    before_stop = before_stop_list[-1] if before_stop_list else None
    after_stop = after_stop_list[0] if after_stop_list else None
    # if there is no before stop, means that the train is not in the first stop
    # so we just return the after stop
    # if no after stop - the reverse
    if not before_stop:
        return [after_stop.stop.stop_pt_lat,after_stop.stop.stop_pt_loc]
    if not after_stop or after_stop == before_stop:
        return [before_stop.stop.stop_pt_lat,before_stop.stop.stop_pt_loc]
    points = json.loads(ShapeJson.objects.get(shape_id=trip.shape_id).points)
    idx_before = find_closest_point_index(trip,points,lat=before_stop.stop.stop_lat,lon=before_stop.stop.stop_lon)
    idx_after = find_closest_point_index(trip,points,lat=after_stop.stop.stop_lat,lon=after_stop.stop.stop_lon)
    delta = float(after_stop.arrival_time - before_stop.departure_time)
    if delta == 0:
        relative = 0
    else:
        relative = (normal_time - before_stop.departure_time) / delta
    num_points = idx_after - idx_before
    idx_result = int(relative*num_points) +  idx_before
    result = points[idx_result]
    return result
    

def find_closest_point_index(trip,points,lat,lon):
    def dist(pt):
        return (pt[0]-lat)*(pt[0]-lat) + (pt[1]-lon)*(pt[1]-lon)
    return min(enumerate(points),key = lambda t : dist(t[1]))[0]
    
def do_search(kind,in_station=None,from_station=None,to_station=None,when=None,before=None,after=None):
    before = int(before)
    after = int(after)
    if kind == 'search-in':
        return do_search_in(in_station,when,before *60,after*60)
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
    normal_time = when.hour * 3660 + when.minute * 60
    stop_times = stop_times.filter(arrival_time__gt=normal_time-before,arrival_time__lt=normal_time+after)
    stop_times = stop_times.order_by('arrival_time')
   
   
    #trips_on_station_in_date = trips_in_station
    #route_ids = models.Trip.objects.filter(trip_id__in=trip_ids).values_list('route_id')
    #routes = models.Route.objects.filter(route_id__in=route_ids)
    
    return stop_times

def do_seatch_between(from_station,to_station,when,before,after):
    pass

def create_all(clean=True,download=True):
    import utils
    cls_list = models.GTFSModel.__subclasses__()  # @UndefinedVariable
    if clean:
        for cls in reversed(cls_list):
            common.ot_utils.delete_from_model(cls)
    if download:
        print 'Downloading gtfs file from web'
        utils.download_gtfs_file()
    dirname = utils.find_gtfs_data_dir()
    
    for cls in cls_list: 
        cls.read_from_csv(dirname)

    create_shape_json()
    
def create_shape_json():
    from models import Shape,ShapeJson
    shape_ids = list(Shape.objects.values_list('shape_id',flat=True).distinct())
    common.ot_utils.delete_from_model(ShapeJson)
    print 'Creating shapes json # of shape_ids = %s' % (len(shape_ids))
    for idx,shape_id in enumerate(shape_ids):
        points = Shape.objects.filter(shape_id=shape_id).order_by('shape_pt_sequence')
        point_list = []
        for point in points:
            point_list.append([point.shape_pt_lat,point.shape_pt_lon])
        ShapeJson(shape_id=shape_id,points=json.dumps(point_list)).save()
        print 'saved %d/%d' % (idx,len(shape_ids)) 

