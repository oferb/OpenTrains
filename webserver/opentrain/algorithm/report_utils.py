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
import calendar

from geo_utils import *
from gtfs_utils import *

def get_location_info_from_device_id(device_id):
    locations = analysis.models.LocationInfo.objects.filter(report__device_id=device_id).order_by('timestamp')
    lat_list = [float(x[0]) for x in list(locations.all().values_list('lat'))]
    lon_list = [float(x[0]) for x in list(locations.all().values_list('lon'))]
    device_accuracies_in_meters = [float(x[0]) for x in list(locations.all().values_list('accuracy'))]
    device_timestamps = [x[0] for x in list(locations.all().values_list('timestamp'))]
    local_time_delta = datetime.timedelta(0,2*3600)    
    device_timestamps = [x + local_time_delta for x in device_timestamps]
    device_accuracies_in_meters = np.array(device_accuracies_in_meters)
    device_accuracies_in_meters[device_accuracies_in_meters > config.max_accuracy_radius_meters] = config.max_accuracy_radius_meters
    device_accuracies_in_meters[device_accuracies_in_meters < config.min_accuracy_radius_meters] = config.min_accuracy_radius_meters

    device_coords = zip(lat_list, lon_list)
    device_coords = np.array(device_coords)
    device_accuracies_in_coords = [meter_distance_to_coord_distance(x) for x in device_accuracies_in_meters]
    return device_coords, device_timestamps, device_accuracies_in_meters, device_accuracies_in_coords

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

def get_device_sampled_tracks_coords(sampled_all_routes_tree, query_coords, device_coords, device_accuracies_in_coords, itertools, config):
    device_sampled_tracks_coords = query_coords(sampled_all_routes_tree, device_coords, device_accuracies_in_coords)
    device_sampled_tracks_coords = sampled_all_routes_tree.data[list(set(list(itertools.chain(*device_sampled_tracks_coords))))]
    device_sampled_tracks_accuracies_in_coords = meter_distance_to_coord_distance(config.route_sampling__min_distance_between_points_meters)
    return device_sampled_tracks_coords, device_sampled_tracks_accuracies_in_coords

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


def get_shape_probabilities(shape_point_tree, shape_int_ids, unique_shape_ids, device_coords, device_accuracies_coords):
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
