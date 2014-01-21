import gtfs.models
from scipy import spatial
import shelve
from Shape import Shape
import os
import config
import numpy as np
import copy

from utils import *
import stops

class Stop(object):
    def __init__( self, id_, name, coords ) :
        self.id_ = id_
        self.name = name
        self.coords = coords

class StopList(list):


    def __init__(self, django_stop_list) :
        stops = gtfs.models.Stop.objects.all();
        stop_ids = [x[0] for x in list(stops.all().values_list('stop_id'))]
        stop_names = [x[0] for x in list(stops.all().values_list('stop_name'))]
        lat_list = [float(x[0]) for x in list(stops.all().values_list('stop_lat'))]
        lon_list = [float(x[0]) for x in list(stops.all().values_list('stop_lon'))] 
        stop_coords = zip(lat_list, lon_list)
        stop_coords = np.array(stop_coords)
        self.point_tree = spatial.cKDTree(stop_coords)
        
        for cur in zip(stop_ids, stop_names, stop_coords):
            stop = Stop(cur[0], cur[1], cur[2])
            self.append(stop)

    def __getstate__(self):
        ret = self.__dict__.copy()
        ret['stop_coords'] = self.point_tree.data
        del ret['point_tree']
        return ret

    def __setstate__(self, dict):
        self.point_tree = spatial.cKDTree(dict['stop_coords'])
        del dict['stop_coords']
        self.__dict__.update(dict)           
    
    def query_stops(self, coords, accuracies)   :
        
        res_coord_ids = query_coords(self.point_tree, coords, accuracies)    

        return res_coord_ids

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


def get_all_stops():
    datafile = shelve.open(os.path.join(config.gtfs_processed_data, 'shelve.data'))

    if True or not datafile.has_key('stopList'):
        gtfs_stops_data = gtfs.models.Stop.objects.all().values_list('stop_id', 'stop_name', 'stop_lat', 'stop_lon')
        datafile['stopList'] = StopList(gtfs_stops_data)
    all_stops = datafile['stopList']
    
    datafile.close() 
    
    return all_stops

stops.all_stops = get_all_stops()