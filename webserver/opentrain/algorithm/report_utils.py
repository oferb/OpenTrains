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

from utils import *
from display_utils import *
import shapes
import stops

def get_shape_probabilities(self, query_coords, query_accuracies_in_coords):

    all_shapes = shapes.all_shapes
    shape_point_tree = all_shapes.point_tree
    
    # res_shape_int_ids is a list of lists of shape_ids, 
    # each inner list contains the indices of shape_ids which have points nearby a query point, 
    # where 'nearby' is according to the accuracies    
    _, res_shape_int_ids = all_shapes.query_all_points(query_coords, query_accuracies_in_coords)
    
    # flatten list
    res_shape_int_ids_flat = list(itertools.chain(*res_shape_int_ids))
    
    # res3 counts the number of times each shape point was seen nearby a query point
    res_shape_counts = np.bincount(res_shape_int_ids_flat)
    
    shape_probs = res_shape_counts/float(len(query_coords))
    
    shape_matches_int_inds = list(np.where(shape_probs > config.shape_probability_threshold)[0])
    shape_matches_inds = [all_shapes[i].id_ for i in shape_matches_int_inds]    
    
    return shape_probs, shape_matches_inds, shape_matches_int_inds


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

def get_device_stops(device_coords, device_timestamps, shape_matches_inds):
    all_stops = stops.all_stops
    query_res = all_stops.query_stops(device_coords, meter_distance_to_coord_distance(config.station_radius_in_meters))
    
    device_stop_int_ids = list(set(np.array(list(itertools.chain(*query_res)))))
    device_stop_ids = [all_stops[i].id_ for i in device_stop_int_ids]
    device_stop_names = [ all_stops[i].name for i in device_stop_int_ids ]
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
    
    # beware of ugly sort, there must be a better way to do this:
    ziplist = zip(device_stops_arrival, device_stop_ids, device_stop_int_ids, device_stop_names, device_stops_departure)   
    ziplist.sort()
    for i, cur in enumerate(ziplist):
        device_stops_arrival[i] = cur[0];
        device_stop_ids[i] = cur[1];
        device_stop_int_ids[i] = cur[2];
        device_stop_names[i] = cur[3];
        device_stops_departure[i] = cur[4];
        
    return device_stop_ids, device_stop_int_ids, device_stop_names, device_stops_arrival, device_stops_departure

def get_device_sampled_tracks_coords(sampled_all_routes_tree, query_coords, device_coords, device_accuracies_in_coords):
    device_sampled_tracks_coords = query_coords(sampled_all_routes_tree, device_coords, device_accuracies_in_coords)
    device_sampled_tracks_coords = sampled_all_routes_tree.data[list(set(list(itertools.chain(*device_sampled_tracks_coords))))]
    device_sampled_tracks_accuracies_in_coords = meter_distance_to_coord_distance(config.route_sampling__min_distance_between_points_meters)
    return device_sampled_tracks_coords, device_sampled_tracks_accuracies_in_coords

def filter_trips_by_shape_date_stops_and_stop_times(start_date, shape_matches_inds, device_stop_ids, device_stop_int_ids, device_stops_arrival, device_stops_departure):
    relevant_services = gtfs.models.Service.objects.filter(start_date = start_date)
    relevant_service_ids = relevant_services.all().values_list('service_id')
    trips = gtfs.models.Trip.objects.filter(shape_id__in=shape_matches_inds, service__in=relevant_service_ids)

    # filter by stop existence and its time frame:
    trips_filtered_by_stops_and_times = trips
    print len(trips_filtered_by_stops_and_times)
    for i in xrange(len(device_stop_ids)):
        trip_stop_times = gtfs.models.StopTime.objects.filter(trip__in = trips_filtered_by_stops_and_times)
        arrival_time__greater_than = device_stops_arrival[i]-datetime.timedelta(seconds=config.late_arrival_max_seconds)
        arrival_time__less_than = device_stops_arrival[i]+datetime.timedelta(seconds=config.early_arrival_max_seconds)
        arrival_time__range = datetime_range_to_db_time(arrival_time__greater_than, arrival_time__less_than)

        departure_time__greater_than = device_stops_departure[i]-datetime.timedelta(seconds=config.late_departure_max_seconds)
        departure_time__less_than = device_stops_departure[i]+datetime.timedelta(seconds=config.early_departure_max_seconds)
        departure_time__range = datetime_range_to_db_time(departure_time__greater_than, departure_time__less_than)
        
        trip_stop_times_for_specific_stop = trip_stop_times.filter(stop = device_stop_ids[i], 
                                                               arrival_time__range=arrival_time__range,
                                                               departure_time__range=departure_time__range)
        trips_filtered_by_stops_and_times = trip_stop_times_for_specific_stop.values_list('trip')
        print len(trips_filtered_by_stops_and_times)
    
    # filter by stop order:
    trip_in_right_direction = []
    for i, t in enumerate(trips_filtered_by_stops_and_times):
        trip_stop_times = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time').values_list('stop')
        trip_stop_times = [x[0] for x in trip_stop_times]
        stop_inds_by_visit_order = [trip_stop_times.index(x) for x in device_stop_ids]
        if strictly_increasing(stop_inds_by_visit_order):
            trip_in_right_direction.append(i)
    
    trips_filtered_by_stops_and_times = [trips_filtered_by_stops_and_times[i] for i in trip_in_right_direction]
    trips_filtered_by_stops_and_times = [x[0] for x in trips_filtered_by_stops_and_times]

    return trips_filtered_by_stops_and_times


def strictly_increasing(L):
    return all(x<y for x, y in zip(L, L[1:])) 