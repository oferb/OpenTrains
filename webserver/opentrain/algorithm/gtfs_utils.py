import gtfs.models
import analysis.models
import numpy as np
from scipy import spatial
import shelve
import matplotlib.pyplot as plt
import simplekml
import config
import itertools
import os
import datetime 

from geo_utils import *

def get_stops():
    stops = gtfs.models.Stop.objects.all();
    stop_ids = [x[0] for x in list(stops.all().values_list('stop_id'))]
    stop_names = [x[0] for x in list(stops.all().values_list('stop_name'))]
    lat_list = [float(x[0]) for x in list(stops.all().values_list('stop_lat'))]
    lon_list = [float(x[0]) for x in list(stops.all().values_list('stop_lon'))] 
    stop_coords = zip(lat_list, lon_list)
    stop_coords = np.array(stop_coords)
    stop_point_tree = spatial.cKDTree(stop_coords)
    return stop_ids, stop_names, stop_coords, stop_point_tree


def get_sampling_of_all_routes(shape_point_tree):
    inds_to_go_over = np.zeros(len(shape_point_tree.data)) == 0
    inds_to_keep = np.zeros(len(shape_point_tree.data)) == -1
    dist_threshold = meter_distance_to_coord_distance(config.route_sampling__min_distance_between_points_meters)
    count = 0
    while count < len(inds_to_go_over):
        while(count < len(inds_to_go_over) and not inds_to_go_over[count]):
            count = count + 1
        if count < len(inds_to_go_over):
            inds_to_keep[count] = True
            inds_to_remove = shape_point_tree.query_ball_point(shape_point_tree.data[count], dist_threshold)
            inds_to_go_over[inds_to_remove] = False
        #inds_to_go_over.pop(inds_to_go_over.index(i))
        
    sampled_all_routes_tree = spatial.cKDTree(shape_point_tree.data[inds_to_keep])
    return inds_to_keep, sampled_all_routes_tree

def get_shape_coords_and_ids():
    return gtfs.models.Shape.objects.all().values_list('shape_id', 'shape_pt_lat', 'shape_pt_lon')


def get_shape_data():
    shape_coords_and_ids = get_shape_coords_and_ids()
    shape_ids = [x[0] for x in list(shape_coords_and_ids.all().values_list('shape_id'))]
    lat_list = [float(x[0]) for x in list(shape_coords_and_ids.all().values_list('shape_pt_lat'))]
    lon_list = [float(x[0]) for x in list(shape_coords_and_ids.all().values_list('shape_pt_lon'))]
    shape_coords = zip(lat_list, lon_list)
    shape_coords = np.array(shape_coords)
    unique_shape_ids = list(set(shape_ids))
    unique_shape_ids.sort()
    shape_int_ids = [unique_shape_ids.index(x) for x in shape_ids]
    shape_int_ids = np.array(shape_int_ids)    
    return shape_ids, shape_coords, unique_shape_ids, shape_int_ids

def get_shape_data_from_cache():
    datafile = shelve.open(os.path.join(config.gtfs_processed_data, 'shelve.data'))
    
    if not datafile.has_key('shape_ids'):
        shape_ids, shape_coords, unique_shape_ids, shape_int_ids = get_shape_data() 
        shape_id_to_route_map, shape_int_id_to_route_id = get_shape_id_to_route_mapping()
        datafile['shape_ids'] = shape_ids
        datafile['shape_coords'] = shape_coords
        datafile['unique_shape_ids'] = unique_shape_ids
        datafile['shape_int_ids'] = shape_int_ids   
        datafile['shape_id_to_route_map'] = shape_id_to_route_map   
    else :
        shape_ids = datafile['shape_ids']
        shape_coords = datafile['shape_coords']
        unique_shape_ids = datafile['unique_shape_ids']
        shape_int_ids = datafile['shape_int_ids']
        shape_id_to_route_map = datafile['shape_id_to_route_map']
        
    datafile.close()  
    return shape_ids, shape_coords, unique_shape_ids, shape_int_ids, shape_id_to_route_map

def get_shape_id_to_route_mapping(do_print=False):
    
    id_list = [x[0] for x in list(gtfs.models.Shape.objects.all().values_list('shape_id'))]
    unique_shape_ids = list(set(id_list))
    unique_shape_ids.sort()
    
    results = zip(unique_shape_ids, [set(gtfs.models.Trip.objects.filter(shape_id=shape_id).values_list('route', 'route__route_long_name')) for shape_id in unique_shape_ids])
    if do_print:
        for result in results:
            print result
    return results


def get_field(services, name):
    service_ids = services.all().values_list(name)
    service_ids = [x[0] for x in service_ids]
    return service_ids


def datetime_to_db_time(adatetime):
    return adatetime.hour * 3600 + 60 * adatetime.minute + adatetime.second

def datetime_range_to_db_time(datetime1, datetime2):
    d1 = datetime_to_db_time(datetime1)
    d2 = datetime_to_db_time(datetime2)
    if d1 > d2: # in gtfs, instead of midnight passing to the next day, you count in more time for the same day, i.e 25:00 instead of 01:00
        d2 = d2 + 24*3600    
    return d1,d2

def db_time_to_datetime(db_time):
    return datetime.time(db_time / 3600 % 24, (db_time % 3600) / 60, db_time % 60)
