import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
import gtfs.models
from scipy import spatial
import shelve
import os
import config
import numpy as np
import copy
import config

from utils import *

NOSTOP = "nostop"

class Stop(object):
    def __init__( self, id_, name, coords ) :
        self.id = id_
        self.name = name
        self.coords = coords

class StopList(dict):

    def __init__(self, django_stop_list) :
        super(StopList, self).__init__()
        
        stops = gtfs.models.Stop.objects.all();
        stops = list(stops)
        
        #stop_ids = [x[0] for x in list(stops.all().values_list('stop_id'))]
        #stop_names = [x[0] for x in list(stops.all().values_list('stop_name'))]
        #lat_list = [float(x[0]) for x in list(stops.all().values_list('stop_lat'))]
        #lon_list = [float(x[0]) for x in list(stops.all().values_list('stop_lon'))] 
        
        self.id_list = []
        stop_coords = []
        for i, gtfs_stop in enumerate(stops):
            coord = (gtfs_stop.stop_lat, gtfs_stop.stop_lon)
            stop = Stop(str(gtfs_stop.stop_id), gtfs_stop.stop_name, coord)
            stop_coords.append(coord)
            self.id_list.append(stop.id)
            self[stop.id] = stop
        
        self.id_list.append(NOSTOP)
        stop_coords = np.array(stop_coords)
        self.point_tree = spatial.cKDTree(stop_coords)               

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
        
        res_coord_int_ids = query_coords(self.point_tree, coords, accuracies)    
        res_coord_ids = [self.id_list[i] for i in res_coord_int_ids]
        return res_coord_ids


def get_all_stops():
    #datafile = shelve.open(config.gtfs_stop_file)

    #if not datafile.has_key('stopList'):
    gtfs_stops_data = gtfs.models.Stop.objects.all().values_list('stop_id', 'stop_name', 'stop_lat', 'stop_lon').order_by('stop_id')
    all_stops = StopList(gtfs_stops_data)
    #all_stops = datafile['stopList']
    
    #datafile.close() 
    
    return all_stops

all_stops = get_all_stops()