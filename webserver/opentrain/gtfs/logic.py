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


def do_search(kind,in_station=None,from_station=None,to_station=None,when=None):
    pass


