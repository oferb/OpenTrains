import gtfs.models
from scipy import spatial
import shelve
import os
import config
import numpy as np
import copy
import stops
import shapes
from sklearn.hmm import MultinomialHMM
from utils import *
from collections import deque
import matplotlib.pyplot as plt
import datetime
from analysis.logic import meter_distance_to_coord_distance
import bssid_tracker

class TrackedStopTime(object):
    def __init__(self, stop_int_id):
        self.stop_int_id = stop_int_id
        self.stop_id = stops.all_stops[stop_int_id].id_
        self.name = stops.all_stops[stop_int_id].name
        self.arrival = None
        self.departure = None
    
    def __str__(self):
        arrival_str = self.arrival.strftime('%H:%M:%S') if self.arrival is not None else '--:--:--'
        departure_str = self.departure.strftime('%H:%M:%S') if self.departure is not None else '--:--:--'
        delta_str = str(self.departure - self.arrival).split('.')[0] if self.departure is not None else '-:--:--'
        return '%s %s %s %s' % (arrival_str, departure_str, delta_str, self.name)
        
     
 
class TrainTracker(object):

    def __init__(self, id_) :
        self.id_ = id_
        self.track_shape_int_ids = []
        self.coords = []
        self.visited_sampled_tracks_point_int_ids = set()
        self.visited_shape_point_ids = set()
        self.shape_counts = np.zeros((len(shapes.all_shapes), 1))
        self.current_stop = None
        
        stop_count = len(stops.all_stops)

        n_components = stop_count+1 # +1 for non-stop
        n_symbols = n_components
        self.non_stop_component_num = n_components-1
        # should probably get these numbers from the data and not guess them :)
        stay_prob = 0.99
        a = np.diag(np.ones(n_components) * stay_prob)
        a[-1,:-1] = (1-stay_prob)/len(a[-1,:-1])
        a[:-1,-1] = (1-stay_prob)
        emissionprob = a
        transmat = a
        startprob = np.ones(n_components)/(n_components) # uniform probability
        self.hmm = MultinomialHMM(n_components,
                                    startprob=startprob,
                                    transmat=transmat)        
        self.hmm._set_emissionprob(emissionprob)

        self.prev_stops = deque(maxlen=3000)
        self.prev_stops_timestamps = deque(maxlen=3000)
        self.stop_times = []
        
    def add(self, report):

        # update train position
        coords_updated = False
        coords = [report.my_loc.lat, report.my_loc.lon]
        res_shape_point_ids, res_shape_int_ids = shapes.all_shapes.query_all_points(coords, report.my_loc.accuracy_in_coords)
        for i in xrange(len(res_shape_point_ids)):
            if res_shape_point_ids[i] not in self.visited_shape_point_ids:
                if not coords_updated: #update if report adds new points on tracks
                    self.coords = coords
                    coords_updated = True
                self.visited_shape_point_ids.add(res_shape_point_ids[i])
                self.shape_counts[res_shape_int_ids[i]] = self.shape_counts[res_shape_int_ids[i]] + 1
        
        # 1) add stop or non-stop to prev_stops and prev_stops_timestamps     
        # 2) set calc_hmm to true if according to wifis and/or location, our state changed from stop to non-stop or vice versa
        calc_hmm = False
        if report.is_station():
            wifis = [x for x in report.wifi_set.all() if x.SSID == 'S-ISRAEL-RAILWAYS']
            wifi_stops_int_ids = set()
            for wifi in wifis:
                if bssid_tracker.tracker.has_bssid_high_confidence(wifi.key):
                    stop_int_id, _ = bssid_tracker.tracker.get_stop_int_id(wifi.key)
                    wifi_stops_int_ids.add(stop_int_id)
            
            wifi_stops_int_ids = np.array(list(wifi_stops_int_ids))

            
            # check all wifis show same station:
            if len(wifi_stops_int_ids) > 0 and np.all(wifi_stops_int_ids == wifi_stops_int_ids[0]):
                self.prev_stops.append(wifi_stops_int_ids[0])
                self.prev_stops_timestamps.append(report.get_timestamp_israel_time())
                if self.current_stop is None:
                    calc_hmm = True
            # "in wifi we trust", "if they have no wifi let them use location"            
            elif report.loc_ts_delta() < config.stop_discovery_location_timeout_seconds:  
                
                coords = [report.my_loc.lat, report.my_loc.lon]
                stop_int_id_list = stops.all_stops.query_stops(coords, meter_distance_to_coord_distance(config.station_radius_in_meters))
                if len(stop_int_id_list) == 1:
                    self.prev_stops.append(stop_int_id_list[0])
                    self.prev_stops_timestamps.append(report.get_timestamp_israel_time())
                    if self.current_stop is None:
                        calc_hmm = True
                    

        else:
            self.prev_stops.append(self.non_stop_component_num)
            self.prev_stops_timestamps.append(report.get_timestamp_israel_time())
            if self.current_stop is not None:
                calc_hmm = True
                
        # calculate hmm to get state_sequence, update stop_times and current_stop if needed
        if calc_hmm:
            logprob, state_sequence = self.hmm.decode(self.prev_stops)
            self.state_sequence_for_debug = state_sequence
            prev_current_stop = self.current_stop
            if state_sequence[-1] == self.non_stop_component_num:
                self.current_stop = None
            else:
                self.current_stop = state_sequence[-1]
            
            prev_timestamp = None
            if prev_current_stop != self.current_stop:
                for i, stop_int_id, timestamp in reversed(zip(range(len(state_sequence)), state_sequence, self.prev_stops_timestamps)):
                    current_stop_component_num = self.non_stop_component_num if self.current_stop is None else self.current_stop
                    # test if this is where we changed states, or this is the first state
                    if (stop_int_id != current_stop_component_num or i == 0):
                        if self.current_stop == None: # we need to set departure
                            self.stop_times[-1].departure = timestamp
                        else: # we need to set arrival
                            if len(self.stop_times) == 0 or self.stop_times[-1].stop_int_id != self.current_stop: # set new stop_time only if for different station
                                stop_time = TrackedStopTime(self.current_stop)
                                self.stop_times.append(stop_time)
                                stop_time.arrival = prev_timestamp if prev_timestamp is not None else timestamp
                        break
                    prev_timestamp = timestamp
                
            
            # grouping stop sequence snippet, not sure if iterator is right approach:
            #from itertools import groupby  
            #groups = groupby(zip(state_sequence, self.prev_stops_timestamps), lambda x: x[0])
            #stop_times = []
            #for stop_int_id,g in groups:
                #if stop_int_id != self.non_stop_component_num:
                    #stop_time = TrackedStopTime(stop_int_id)
                    #stop_times.append(stop_time)
                    #stop_time.arrival = g.next()
                    #for x in g:
                        #stop_time.departure = x
    
    # None means we cannot find a reasonable trip list
    # empty list means there are no trips that fit this tracker
    def get_possible_trips(self, print_debug_info=False):
        if len(self.stop_times) == 0:
            return None
        start_date = self.stop_times[0].arrival.strftime("%Y-%m-%d")
        shape_matches_inds = self.get_shape_ids_with_high_probability()
        relevant_services = gtfs.models.Service.objects.filter(start_date = start_date)
        relevant_service_ids = relevant_services.all().values_list('service_id')
        trips = gtfs.models.Trip.objects.filter(shape_id__in=shape_matches_inds, service__in=relevant_service_ids)
    
        # filter by stop existence and its time frame:
        trips_filtered_by_stops_and_times = trips
        if print_debug_info:
            print len(trips_filtered_by_stops_and_times)
        for tracked_stop_time in self.stop_times:
            trip_stop_times = gtfs.models.StopTime.objects.filter(trip__in = trips_filtered_by_stops_and_times)
            arrival_time__greater_than = tracked_stop_time.arrival-datetime.timedelta(seconds=config.late_arrival_max_seconds)
            arrival_time__less_than = tracked_stop_time.arrival+datetime.timedelta(seconds=config.early_arrival_max_seconds)
            arrival_time__range = datetime_range_to_db_time(arrival_time__greater_than, arrival_time__less_than)
    
            if tracked_stop_time.departure is not None:
                departure_time__greater_than = tracked_stop_time.departure-datetime.timedelta(seconds=config.late_departure_max_seconds)
                departure_time__less_than = tracked_stop_time.departure+datetime.timedelta(seconds=config.early_departure_max_seconds)
                departure_time__range = datetime_range_to_db_time(departure_time__greater_than, departure_time__less_than)
            
                trip_stop_times_for_specific_stop = trip_stop_times.filter(stop = tracked_stop_time.stop_id, 
                                                                           arrival_time__range=arrival_time__range,
                                                                           departure_time__range=departure_time__range)
            
            else:
                trip_stop_times_for_specific_stop = trip_stop_times.filter(stop = tracked_stop_time.stop_id, 
                                                                           arrival_time__range=arrival_time__range)                
                
            trips_filtered_by_stops_and_times = trip_stop_times_for_specific_stop.values_list('trip')

            if print_debug_info:
                print len(trips_filtered_by_stops_and_times)
        
        # filter by stop order:
        trip_in_right_direction = []
        for i, t in enumerate(trips_filtered_by_stops_and_times):
            trip_stop_times = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time').values_list('stop')
            trip_stop_times = [x[0] for x in trip_stop_times]
            stop_inds_by_visit_order = [trip_stop_times.index(x) for x in [x.stop_id for x in self.stop_times]]
            if is_increasing(stop_inds_by_visit_order):
                trip_in_right_direction.append(i)
        
        trips_filtered_by_stops_and_times = [trips_filtered_by_stops_and_times[i][0] for i in trip_in_right_direction]
        
        arrival_delta_abs_sums = []
        departure_delta_abs_sums = []
        for t in trips_filtered_by_stops_and_times:
            stop_times = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time').values_list('stop', 'arrival_time', 'departure_time')
            arrival_delta_abs_sum = 0
            departure_delta_abs_sum = 0
            for tracked_stop_time in self.stop_times:
                stop_time = [x for x in stop_times if x[0] == tracked_stop_time.stop_id][0]
                arrival_delta_seconds = stop_time[1] - datetime_to_db_time(tracked_stop_time.arrival)
                departure_delta_seconds = stop_time[2] - datetime_to_db_time(tracked_stop_time.departure)
                arrival_delta_abs_sum += abs(arrival_delta_seconds)
                departure_delta_abs_sum += abs(departure_delta_seconds)
            arrival_delta_abs_sums.append(arrival_delta_abs_sum)
            departure_delta_abs_sums.append(departure_delta_abs_sum)
        
        # sort results by increasing arrival time 
        trips_filtered_by_stops_and_times = [x for (y,x) in sorted(zip(arrival_delta_abs_sums,trips_filtered_by_stops_and_times))]
        return trips_filtered_by_stops_and_times

     
    def get_shape_probs(self):
        return self.shape_counts/float(max(self.shape_counts))

    def get_shape_ids_with_high_probability(self):
        shape_int_ids = np.where(self.get_shape_probs() >= config.shape_probability_threshold)[0]
        shape_ids = [shapes.all_shapes[x].id_ for x in shape_int_ids]
        return shape_ids
    
    def print_possible_trips(self):
        trips = self.get_possible_trips()
        print 'Trip count = %d' %(len(trips))
        for t in trips:
            trip_stop_times = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time')
            print "trip id: %s" % (t)
            for x in trip_stop_times:
                print db_time_to_datetime(x.arrival_time), db_time_to_datetime(x.departure_time), x.stop
            print        
            
    def print_tracked_stop_times(self):
        for tracked_stop_time in self.stop_times:
            print tracked_stop_time
        