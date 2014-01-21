import gtfs.models
from scipy import spatial
import shelve
import os
import config
import numpy as np
import copy
from shapes import ShapeList
import shapes

from utils import *


class TrackedItem(object):
    def __init__(self, router_id, device_id, device_timestamp, server_timestamp, coords_timestamp, coords, accuracy_in_coords, accuracy_in_meters):
        self.router_id = router_id      
        self.device_id = device_id
        self.device_timestamp = device_timestamp
        self.server_timestamp = server_timestamp
        self.coords_timestamp = coords_timestamp
        self.coords = coords
        self.accuracy_in_coords = accuracy_in_coords
        self.accuracy_in_meters = accuracy_in_meters

class TrackedStopTime(object):
    def __init__(self, stop):
        self.stop = stop
        self.timestamps = []
 
    #def add_timestamp(timestamp):
        
 
class TrainTracker(object):

    def __init__(self, id_) :
        self.id_ = id_
        self.track_shape_int_ids = []
        self.coords = []
        self.visited_sampled_tracks_point_int_ids = set()
        self.visited_shape_point_ids = set()
        self.shape_counts = np.zeros((len(shapes.all_shapes), 1))
        
    def add(self, item):
        # update train position
        
        #sampled_tracks_point_int_ids, _ = shapes.all_shapes.query_sampled_points(item.coords, item.accuracy_in_coords)
        #sampled_tracks_point_int_ids = set(sampled_tracks_point_int_ids)
        #sampled_tracks_point_int_ids -= self.visited_sampled_tracks_point_int_ids
        #if sampled_tracks_point_int_ids is not None and len(sampled_tracks_point_int_ids) != 0:
        self.coords = item.coords
        #self.visited_sampled_tracks_point_int_ids |= sampled_tracks_point_int_ids
        res_shape_point_ids, res_shape_int_ids = shapes.all_shapes.query_all_points(item.coords, item.accuracy_in_coords)
        for i in xrange(len(res_shape_point_ids)):
            if res_shape_point_ids[i] not in self.visited_shape_point_ids:
                self.visited_shape_point_ids.add(res_shape_point_ids[i])
                self.shape_counts[res_shape_int_ids[i]] = self.shape_counts[res_shape_int_ids[i]] + 1
        
        # todo: add stops in online fashion:
        #all_stops = stops.all_stops
        #query_res = all_stops.query_stops(item.coords, meter_distance_to_coord_distance(config.station_radius_in_meters))
                  
            
    def get_shape_probs(self):
        return self.shape_counts/float(max(self.shape_counts))
