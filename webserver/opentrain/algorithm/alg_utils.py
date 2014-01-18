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
from gtfs_utils import *
from report_utils import *


def query_coords(point_tree, query_coords, query_accuracies):
    if isinstance( query_accuracies, ( int, long, float ) ):
        res = point_tree.query_ball_point(query_coords, query_accuracies)
    else:
        res = [point_tree.query_ball_point(query_coords[i], query_accuracies[i]) for i in xrange(len(query_accuracies))]
    return res


def get_shape_probabilities_old(shape_point_tree, device_coords, device_accuracies_coords):
    # res is a list of lists of query_coords, 
    # each inner list contains the indices of nearby shape points where nearby is according to the accuracies
    res = query_coords(shape_point_tree, device_coords, device_accuracies_in_coords)
    
    # res2 is a list of shape points that were near some query point
    res2 = list(itertools.chain(*res))
    
    # res3 counts the number of times each shape point was seen nearby a query point
    res3 = np.bincount(res2)
    # res4 adds zeros so we get a full length list the length of the number of shape points
    res4 = list(res3) + [0]*(len(shape_ids)-len(res3))
    res4 = np.array(res4)
    # res4 holds has the number of times each shape_point was located within accuracy distance from a query point
    
    #plot_coords(shape_point_tree.data[::10], colors=res4[::10], axis = ax1)
    res4_bool = res4>0
    
    res_accumarray = np.bincount(shape_int_ids, res4_bool).reshape((len(unique_shape_ids),1))
    print_array(res_accumarray)


def get_shape_probabilities(shape_point_tree, device_coords, device_accuracies_coords):
    # res is a list of lists of query_coords, 
    # each inner list contains the indices of nearby shape points where nearby is according to the accuracies
    res = query_coords(shape_point_tree, device_coords, device_accuracies_coords)    

    for i in xrange(len(res)):
        res[i] = list(set(shape_int_ids[res[i]]))

    res2 = list(itertools.chain(*res))
    
    # res3 counts the number of times each shape point was seen nearby a query point
    res3 = np.bincount(res2)
    
    shape_probs = res3.astype('float')/len(device_coords)    

    shape_matches_int_inds = list(np.where(shape_probs > config.shape_probability_threshold)[0])
    shape_matches_inds = [unique_shape_ids[i] for i in shape_matches_int_inds]    
    
    #plot_and_save_shape_matches(shape_point_tree, shape_int_ids, device_route_coords, shape_probs)

    return shape_probs, shape_matches_inds, shape_matches_int_inds


def datetime_to_db_time(adatetime):
    return adatetime.hour * 60 + adatetime.minute

def db_time_to_datetime(db_time):
    return datetime.time(db_time/60 % 24, db_time%60)

def get_device_sampled_tracks_coords(sampled_all_routes_tree, query_coords, device_coords, device_accuracies_in_coords, itertools, config):
    device_sampled_tracks_coords = query_coords(sampled_all_routes_tree, device_coords, device_accuracies_in_coords)
    device_sampled_tracks_coords = sampled_all_routes_tree.data[list(set(list(itertools.chain(*device_sampled_tracks_coords))))]
    device_sampled_tracks_accuracies_in_coords = meter_distance_to_coord_distance(config.route_sampling__min_distance_between_points_meters)
    return device_sampled_tracks_coords, device_sampled_tracks_accuracies_in_coords

def get_device_stops(device_coords, device_timestamps, shape_matches_inds, stop_ids, stop_names, stop_point_tree):
    
    query_res = query_coords(stop_point_tree, device_coords, meter_distance_to_coord_distance(config.station_radius_in_meters))
    
    device_stop_int_ids = list(set(np.array(list(itertools.chain(*query_res)))))
    device_stop_ids = [stop_ids[i] for i in device_stop_int_ids]
    device_stop_names = [ stop_names[i] for i in device_stop_int_ids ]
    device_stops_arrival = []
    device_stops_departure = []
    device_stops_duration = []
    for i in xrange(len(device_stop_int_ids)):
        stop_int_id = device_stop_int_ids[i]
        stop_timestamp_inds = [i for i in xrange(len(query_res)) if (stop_int_id in query_res[i])]
        stop_timestamps = [device_timestamps[i] for i in stop_timestamp_inds]
        stop_timestamps.sort()
        device_stops_arrival.append(stop_timestamps[0])
        device_stops_departure.append(stop_timestamps[-1])
        device_stops_duration.append(device_stops_departure[-1] - device_stops_arrival[-1])
        print device_stops_duration[-1]
        #plt.scatter(stop_timestamps, np.zeros(len(stop_timestamps)))
    return device_stop_ids, device_stop_int_ids, device_stop_names, device_stops_arrival, device_stops_departure

def filter_trips_by_shape_date_stops_and_stop_times(start_date, shape_matches_inds, device_stop_ids, device_stop_int_ids, device_stops_arrival, device_stops_departure):
    relevant_services = gtfs.models.Service.objects.filter(start_date = start_date)
    relevant_service_ids = relevant_services.all().values_list('service_id')
    trips = gtfs.models.Trip.objects.filter(shape_id__in=shape_matches_inds, service__in=relevant_service_ids)
    trips_filtered_by_stops_and_times = trips
    print len(trips_filtered_by_stops_and_times)
    for i in xrange(len(device_stop_ids)):
        trip_stop_times = gtfs.models.StopTime.objects.filter(trip__in = trips_filtered_by_stops_and_times)
        arrival_time__greater_than = device_stops_arrival[i]-datetime.timedelta(seconds=config.late_arrival_max_seconds)
        arrival_time__less_than = device_stops_arrival[i]+datetime.timedelta(seconds=config.early_arrival_max_seconds)
        arrival_time__range = [datetime_to_db_time(arrival_time__greater_than), datetime_to_db_time(arrival_time__less_than)]
        departure_time__greater_than = device_stops_departure[i]-datetime.timedelta(seconds=config.late_departure_max_seconds)
        departure_time__less_than = device_stops_departure[i]+datetime.timedelta(seconds=config.early_departure_max_seconds)
        departure_time__range = [datetime_to_db_time(departure_time__greater_than), datetime_to_db_time(departure_time__less_than)]
        
        trip_stop_times_for_specific_stop = trip_stop_times.filter(stop = device_stop_ids[i], 
                                                               arrival_time__range=arrival_time__range,
                                                               departure_time__range=departure_time__range)
        trips_filtered_by_stops_and_times = trip_stop_times_for_specific_stop.values_list('trip')
        print len(trips_filtered_by_stops_and_times)
    return trips_filtered_by_stops_and_times


# load gtfs data    
shape_ids, shape_coords, unique_shape_ids, shape_int_ids, shape_id_to_route_map = get_shape_data_from_cache() 
shape_point_tree = spatial.cKDTree(shape_coords)
sampled_all_routes_inds, sampled_all_routes_tree = get_sampling_of_all_routes(shape_point_tree)
stop_ids, stop_names, stop_coords, stop_point_tree = get_stops()

# load query data 
device_id = '02090d12'
device_coords, device_timestamps, device_accuracies_in_meters, device_accuracies_in_coords = get_location_info_from_device_id(device_id)
device_sampled_tracks_coords, device_sampled_tracks_accuracies_in_coords = get_device_sampled_tracks_coords(sampled_all_routes_tree, query_coords, device_coords, device_accuracies_in_coords, itertools, config)

# find relevant shapes
shape_probs, shape_matches_inds, shape_matches_int_inds = get_shape_probabilities(shape_point_tree, device_sampled_tracks_coords, device_sampled_tracks_accuracies_in_coords)
#

# Eran's trip was 13/1/2014
start_date = device_timestamps[0].strftime("%Y-%m-%d")
device_stop_ids, device_stop_int_ids, device_stop_names, device_stops_arrival, device_stops_departure = get_device_stops(device_coords, device_timestamps, shape_matches_inds, stop_ids, stop_names, stop_point_tree)

trips_filtered_by_stops_and_times = filter_trips_by_shape_date_stops_and_stop_times(start_date, shape_matches_inds, device_stop_ids, device_stop_int_ids, device_stops_arrival, device_stops_departure)

for t in trips_filtered_by_stops_and_times:
    trip_stop_times = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time')
    print "trip id: %s" % (t[0])
    for x in trip_stop_times:
        print db_time_to_datetime(x.arrival_time), db_time_to_datetime(x.departure_time), x.stop
    print


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
