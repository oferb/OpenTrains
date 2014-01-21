""" comment 
export DJANGO_SETTINGS_MODULE="opentrain.settings"
"""
import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
#/home/oferb/docs/train_project/OpenTrains/webserver
import gtfs.models
import analysis.models
import numpy as np
from scipy import spatial
import shelve
import matplotlib.pyplot as plt
import simplekml
import config
import itertools
import datetime
from unittest import TestCase
import unittest

from display_utils import *
from export_utils import *
from report_utils import *
import shapes
from train_tracker import TrackedItem
from train_tracker import TrainTracker

class train_tracker_test(TestCase):
    
    def match_device_id2(self, device_id, do_print=False):
        sampled_all_routes_tree = shapes.all_shapes.sampled_point_tree
        shape_point_tree = shapes.all_shapes.point_tree
        
        shape_int_ids = []
        device_coords, device_timestamps, device_accuracies_in_meters, device_accuracies_in_coords = get_location_info_from_device_id(device_id)
    
        tracker = TrainTracker('train_id')
        for i in xrange(len(device_coords)):

            trackedItem = TrackedItem("", device_id, device_timestamps[i], 
                                     server_timestamp=0, 
                                     coords_timestamp=0, 
                                     coords=device_coords[i], 
                                     accuracy_in_coords=device_accuracies_in_coords[i], 
                                     accuracy_in_meters=device_accuracies_in_meters[i])
            tracker.add(trackedItem)
        
        
        print tracker.get_shape_probs()
        device_sampled_tracks_coords, device_sampled_tracks_accuracies_in_coords = get_device_sampled_tracks_coords(sampled_all_routes_tree, query_coords, device_coords, device_accuracies_in_coords)
            
        # Matching trip
        shape_probs, shape_matches_inds, shape_matches_int_inds = get_shape_probabilities(shape_int_ids, device_sampled_tracks_coords, device_sampled_tracks_accuracies_in_coords)
        if False:
            plot_and_save_shape_matches(shape_point_tree, sampled_all_routes_tree, shape_int_ids, device_coords, shape_probs)
    
        start_date = device_timestamps[0].strftime("%Y-%m-%d")
        device_stop_ids, device_stop_int_ids, device_stop_names, device_stops_arrival, device_stops_departure = get_device_stops(device_coords, device_timestamps, shape_matches_inds)
        trips_filtered_by_stops_and_times = filter_trips_by_shape_date_stops_and_stop_times(start_date, shape_matches_inds, device_stop_ids, device_stop_int_ids, device_stops_arrival, device_stops_departure)
    
        if do_print:
            for t in trips_filtered_by_stops_and_times:
                trip_stop_times = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time')
                print "trip id: %s" % (t)
                for x in trip_stop_times:
                    print db_time_to_datetime(x.arrival_time), db_time_to_datetime(x.departure_time), x.stop
                print
        
            for cur in zip(device_stops_arrival, device_stops_departure, device_stop_names):
                print cur[0].strftime('%H:%M:%S'), cur[1].strftime('%H:%M:%S'), cur[2]
            
            save_to_kml(device_coords, os.path.join(config.output_data, "shape_%s.kml" % (device_id)))  
          
        return trips_filtered_by_stops_and_times

    def test_tracker_on_device(self):
        
        device_id = '02090d12' # Eran's trip
        trips = self.match_device_id2(device_id)
        
if __name__ == '__main__':
    unittest.main()