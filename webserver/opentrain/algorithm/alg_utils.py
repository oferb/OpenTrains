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

from display_utils import *
from export_utils import *
from report_utils import *
import shapes

def match_device_id(device_id, do_print=False):
    sampled_all_routes_tree = shapes.all_shapes.sampled_point_tree
    shape_point_tree = shapes.all_shapes.point_tree
    
    shape_int_ids = []
    device_coords, device_timestamps, device_accuracies_in_meters, device_accuracies_in_coords = get_location_info_from_device_id(device_id)
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





if False:
    
    # Loading trip
    #device_id = '02090d12' # Eran's trip
    #device_id = 'f752c40d' # Ofer's trip
    device_id = '1cb87f1e' # Udi's trip
    trips_filtered_by_stops_and_times = match_device_id(device_id, sampled_all_routes_tree, shape_point_tree, shape_int_ids, unique_shape_ids, stop_point_tree, stop_ids, stop_names)
    
    
    # TODO: check that departure_time-arrival_time (stop time) make sense, especially for first and last stations.
    # TODO: check earliest and latest train, because of the 5am day change in user_id.
    # TODO: make everything OOP
    
# some code snippets:
if False:
    
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plot_coords(sampled_all_routes_tree.data, edgecolor='b', axis = ax1)
    plot_coords(device_sampled_tracks_coords, edgecolor='r', axis = ax1)
    #save_to_kml(device_coords, os.path.join(config.output_data, "shape_%s.kml" % (device_id)))
    
    device_coords_short = device_coords[750:]
    device_accuracies_coords_short = device_accuracies_in_coords[750:]
    device_accuracies_meters_short = device_accuracies_in_meters[750:]
    #save_to_kml(device_coords_short, os.path.join(config.output_data, "shape_%s_short.kml" % (device_id)))


if False:
    # plot query points unmatched to shape_id
    shape_id = 10
    device_coords_no_route_point_matches = [True if shape_id not in x else False for x in res]
    plot_coords(device_coords[np.where(device_coords_no_route_point_matches)])
    save_to_kml(device_coords[np.where(device_coords_no_route_point_matches)], os.path.join(config.output_data, "test_%s_short.kml" % (device_id)))
