import gtfs.models
import analysis.models
import numpy as np
from scipy import spatial
import shelve
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass
import simplekml
import config
import itertools
import os



def print_all(route_id):
    results = gtfs.models.Trip.objects.filter(route_id=route_id)
    for result in results:
        print result.trip_id

def print_all_stop_names():
    results = gtfs.models.Stop.objects.all().values_list('stop_name')
    for result in results:
        print result

def get_all_routes(do_print=True):
    routes = gtfs.models.Route.objects.all().values_list('route_id', 'route_long_name')
    if do_print:
        for route in routes:
            print route
    return routes

def print_all_shape_long_lat(shape_id):
    results = gtfs.models.Shape.objects.filter(shape_id=shape_id)
    for result in results:
        print '%s, %s, %s' % (result.shape_pt_sequence, result.shape_pt_lat, result.shape_pt_lon)
        
def print_all_shape_ids():
    results = set(gtfs.models.Shape.objects.all().values_list('shape_id'))
    for result in results:
        print result
        
def print_device_id(device_id):
    count = 0
    results = analysis.models.Report.objects.filter(device_id=device_id)
    for result in results:
        count = count + 1
        print("%d,%s,%s" % (count, result.my_loc.lat, result.my_loc.lon))

def print_all_devices():
    results = analysis.models.Report.objects.all().values_list('device_id')
    for result in results:
        print result

def print_device_wifis(device_id):
    results = analysis.models.Report.objects.all()
    for result in results:
        print result, result.wifi_set.all()

#print_all_stop_names();
#print_device_id("02090d12")
#print_device_id("aaa")
#print_all_devices("aaa")
#print_device_wifis("aaa")
#print_all_route_long_name()
#print_all_shape_long_lat('51_00001')

#print_all_shape_ids()