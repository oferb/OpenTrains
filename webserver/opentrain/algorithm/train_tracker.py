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
from common.ot_utils import *
from collections import deque
from common import ot_utils
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass
import datetime
import bssid_tracker 
from redis_intf.client import get_redis_pipeline, get_redis_client, load_by_key, save_by_key 
import json
from utils import enum

TRACKER_TTL = 1 * 60
TRACKER_REPORT_FOR_TRIP_COUNT_LOWER_THAN = 3
HISTORY_LENGTH = 1000

class TrackedStopTime(object):
    def __init__(self, stop_id):
        self.stop_id = stop_id
        self.stop_id = stops.all_stops[stop_id].id
        self.name = stops.all_stops[stop_id].name
        self.arrival = None
        self.departure = None
    
    def __str__(self):
        return TrackedStopTime.get_str(self.arrival, self.departure, self.name)

    @staticmethod
    def get_str(arrival, departure, name):
        arrival_str = arrival.strftime('%H:%M:%S') if arrival is not None else '--:--:--'
        departure_str = departure.strftime('%H:%M:%S') if departure is not None else '--:--:--'
        delta_str = str(departure - arrival).split('.')[0] if departure is not None else '-:--:--'
        return '%s %s %s %s' % (arrival_str, departure_str, delta_str, name)
        

# relevant_services = services for today. used to filter trips by day
def get_train_tracker_relevant_services_key(tracker_id):
    return "train_tracker:%s:relevant_services" % (tracker_id)

def get_train_tracker_coords_key(tracker_id):
    return "train_tracker:%s:coords" % (tracker_id)

def get_train_tracker_visited_shape_sampled_point_ids_key(tracker_id):
    return "train_tracker:%s:visited_shape_sampled_point_ids" % (tracker_id)   

def get_train_tracker_trip_ids_key(tracker_id):
    return "train_tracker:%s:trip_ids" % (tracker_id)

def get_train_tracker_trip_ids_deviation_seconds_key(tracker_id):
    return "train_tracker:%s:trip_ids_deviation_seconds" % (tracker_id)

def get_train_tracker_current_stop_id_key(tracker_id):
    return "train_tracker:%s:current_stop_id" % (tracker_id)

def get_train_tracker_timestamp_sorted_stop_ids_key(tracker_id):
    return "train_tracker:%s:timestamp_sorted_stop_ids" % (tracker_id)

def get_train_tracker_tracked_stops_key(tracker_id):
    return "train_tracker:%s:tracked_stops" % (tracker_id)

def get_train_tracker_tracked_stops_prev_stops_counter_key(tracker_id):
    return "train_tracker:%s:tracked_stops:prev_stops_counter" % (tracker_id)

def get_train_tracker_prev_stops_counter_key(tracker_id):
    return "train_tracker:%s:prev_stops_counter" % (tracker_id)

def get_train_tracker_counters_key(tracker_id):
    return "train_tracker:%s:counters" % (tracker_id)

def get_train_tracker_total_key(tracker_id):
    return "train_tracker:%s:total" % (tracker_id)

def get_current_trip_id_coords_key(trip_id):
    return 'current_trip_id:coords:%s' % (trip_id)

def get_current_trip_id_coords_timestamp_key(trip_id):
    return 'current_trip_id:coords_timestamp:%s' % (trip_id)

def get_current_trip_id_report_timestamp_key(trip_id):
    return 'current_trip_id:report_timestamp:%s' % (trip_id)


def setup_hmm():
    stop_count = len(stops.all_stops)

    n_components = stop_count+1 # +1 for non-stop
    n_symbols = n_components
    hmm_non_stop_component_num = n_components-1
    # should probably get these numbers from the data and not guess them :)
    stay_prob = 0.99
    a = np.diag(np.ones(n_components) * stay_prob)
    a[-1,:-1] = (1-stay_prob)/len(a[-1,:-1])
    a[:-1,-1] = (1-stay_prob)
    emissionprob = a
    transmat = a
    startprob = np.ones(n_components)/(n_components) # uniform probability
    hmm = MultinomialHMM(n_components,
                                startprob=startprob,
                                transmat=transmat)        
    hmm._set_emissionprob(emissionprob)
    
    return hmm, hmm_non_stop_component_num

def add_report_to_tracker(tracker_id, report):
    if not load_by_key(get_train_tracker_relevant_services_key(tracker_id)):
        start_date = report.timestamp.strftime("%Y-%m-%d")
        relevant_services = gtfs.models.Service.objects.filter(start_date = start_date)
        relevant_service_ids = [x[0] for x in relevant_services.all().values_list('service_id')]
        save_by_key(get_train_tracker_relevant_services_key(tracker_id), relevant_service_ids)
         
    # update train position
    if report.get_my_loc():
        try_update_coords(report, tracker_id)
        
        ##commented out below is code that filters trips based on shape
        #coords_updated = False
        #p = get_redis_pipeline()
        #p.zincrby("train_tracker:%s:counters" % (tracker_id), res_shape_ids[i], inc_by)
        #p.incr("train_tracker:%s:total" % (tracker_id), inc_by)
        #p.execute()        

        #for i in xrange(len(res_shape_point_ids)):
            #cl = get_redis_client()
            #if cl.sadd("train_tracker:%s:visited_shape_point_ids" % (tracker_id), res_shape_point_ids[i]) == 0:
                #if not coords_updated: #update if report adds new points on tracks
                    #self.coords = coords
                    #coords_updated = True
                #p = get_redis_pipeline()
                #p.zincrby("train_tracker:%s:counters" % (tracker_id), res_shape_ids[i], 1)
                #p.incr("train_tracker:%s:total" % (tracker_id))
                #p.execute()
                ##self.shape_counts[res_shape_ids[i]] = self.shape_counts[res_shape_ids[i]] + 1
        
        # 1) add stop or non-stop to prev_stops and prev_stops_timestamps     
        # 2) set calc_hmm to true if according to wifis and/or location, our state changed from stop to non-stop or vice versa
    prev_current_stop_id_by_hmm = cl.get(get_train_tracker_current_stop_id_key(tracker_id))
      
    if not prev_current_stop_id_by_hmm:
        prev_state = tracker_states.INITIAL
    elif prev_current_stop_id_by_hmm == stops.NOSTOP:
        prev_state = tracker_states.NOSTOP
    else:
        prev_state = tracker_states.STOP

    stop_id = try_get_stop_id(report)
    if not stop_id:
        current_state = tracker_states.UNKNOWN
    elif stop_id == nostop_id:
        current_state = tracker_states.NOSTOP
    else:
        current_state = tracker_states.STOP

    if current_state != tracker_states.UNKNOWN:
        timestamp = report.get_timestamp_israel_time()
        prev_stop_id = add_prev_stop(tracker_id, stop_id, timestamp)
        
    # calculate hmm to get state_sequence, update stop_times and current_stop if needed
    if  current_state != tracker_states.UNKNOWN and prev_state != current_state:

        prev_stops_and_timestamps = cl.zrange(get_train_tracker_timestamp_sorted_stop_ids_key(tracker_id), 0, -1, withscores=True)
        prev_stop_ids_order = [int(x[0].split("_")[0]) for x in prev_stops_and_timestamps]
        prev_stops_and_timestamps = [x for (y,x) in sorted(zip(prev_stop_ids_order,prev_stops_and_timestamps))]
        
        prev_stop_ids = [x[0].split("_")[1] for x in prev_stops_and_timestamps]
        
        prev_stop_int_ids = np.array([stops.all_stops.id_list.index(x) for x in prev_stop_ids])
        #assert np.array_equal(prev_stop_int_ids, np.array(self.prev_stops))
        prev_stop_hmm_logprob, prev_stop_int_ids_by_hmm = hmm.decode(prev_stop_int_ids)
        prev_stop_int_ids_by_hmm_for_debug = prev_stop_int_ids_by_hmm
        
        # update current_stop_id_by_hmm and current_state by hmm:        
        current_stop_id_by_hmm = stops.all_stops.id_list[prev_stop_int_ids_by_hmm[-1]]
        cl.set(get_train_tracker_current_stop_id_key(tracker_id), current_stop_id_by_hmm)
        if current_stop_id_by_hmm == stops.NOSTOP:
            current_state = tracker_states.NOSTOP
        else:
            current_state = tracker_states.STOP

        if prev_state != current_state: # change in state
            prev_stops_by_hmm = [stops.all_stops.id_list[x] for x in prev_stop_int_ids_by_hmm]
            prev_stops_timestamps = [ot_utils.unix_time_to_localtime((x[1])) for x in prev_stops_and_timestamps]
            index_of_oldest_current_state = max(0, find_index_of_first_consecutive_value(prev_stops_by_hmm, len(prev_stops_by_hmm)-1))
            index_of_most_recent_previous_state = index_of_oldest_current_state-1
              
            if current_state == tracker_states.NOSTOP:
                stop_id = prev_stops_by_hmm[index_of_most_recent_previous_state]
                unix_timestamp = ot_utils.dt_time_to_unix_time(prev_stops_timestamps[index_of_most_recent_previous_state])

                if prev_state == tracker_states.INITIAL:
                    pass #do nothing
                else: # previous_state == tracker_states.STOP - need to set stop_time departure
                    stop_time = cl.zrange(get_train_tracker_tracked_stops_key(tracker_id), -1, -1, withscores=True)
                    departure_unix_timestamp = unix_timestamp
                    stop_id_and_departure_time = "%s_%d" % (prev_current_stop_id_by_hmm, departure_unix_timestamp)
                    update_stop_time(tracker_id, prev_stop_id, stop_time[0][1], stop_id_and_departure_time)
                    update_trips(tracker_id)
            else: # current_state == tracker_states.STOP
                stop_id = prev_stops_by_hmm[index_of_oldest_current_state]
                unix_timestamp = ot_utils.dt_time_to_unix_time(prev_stops_timestamps[index_of_oldest_current_state])
                
                arrival_unix_timestamp = unix_timestamp
                stop_id_and_departure_time = "%s_" % (current_stop_id_by_hmm)
                update_stop_time(tracker_id, prev_stop_id, arrival_unix_timestamp, stop_id_and_departure_time)
                update_trips(tracker_id)
                    
            prev_timestamp = unix_timestamp
                
        print_tracked_stop_times(tracker_id)

def try_update_coords(report, tracker_id):
    loc = report.get_my_loc()
    coords = [loc.lat, loc.lon]
    res_shape_sampled_point_ids, _ = shapes.all_shapes.query_sampled_points(coords, loc.accuracy_in_coords)
     
    added_count = cl.sadd(get_train_tracker_visited_shape_sampled_point_ids_key(tracker_id), res_shape_sampled_point_ids)

    trips = load_by_key(get_train_tracker_trip_ids_key(tracker_id))
    trip = trips[0] if trips else None
    if added_count > 0:
        
        save_by_key(get_train_tracker_coords_key(tracker_id), coords, cl=p)
        
        if trip is not None and len(trips) <= TRACKER_REPORT_FOR_TRIP_COUNT_LOWER_THAN:
            save_by_key(get_current_trip_id_coords_key(trip), coords, timeout=TRACKER_TTL, cl=p)
            save_by_key(get_current_trip_id_coords_timestamp_key(trip), ot_utils.dt_time_to_unix_time(report.timestamp), timeout=TRACKER_TTL, cl=p)
        p.execute()              
    
    if trip is not None:    
        cl.setex(get_current_trip_id_report_timestamp_key(trip), TRACKER_TTL, ot_utils.dt_time_to_unix_time(report.timestamp))

def try_get_stop_id(report):
    if report.is_station():
        wifis = [x for x in report.get_wifi_set_all() if x.SSID == 'S-ISRAEL-RAILWAYS']
        wifi_stops_ids = set()
        for wifi in wifis:
            if bssid_tracker.tracker.has_bssid_high_confidence(wifi.key):
                stop_id ,_ ,_ = bssid_tracker.tracker.get_stop_id(wifi.key)
                wifi_stops_ids.add(stop_id)
        
        wifi_stops_ids = np.array(list(wifi_stops_ids))
        
        # check all wifis show same station:
        if len(wifi_stops_ids) > 0 and np.all(wifi_stops_ids == wifi_stops_ids[0]):
            stop_id = wifi_stops_ids[0]
        else:
            stop_id = None          
    else:
        stop_id = nostop_id
           
    return stop_id

def find_index_of_first_consecutive_value(values, start_index):
    res = None
    for i in reversed(range(start_index)):
        if values[i] != values[start_index]:
            res = i+1
            break
        elif i == 0:
            res = 0
            break        
    
    return res

def update_trips(tracker_id):
    trips, time_deviation_in_seconds = get_possible_trips(tracker_id)
    #if len(trips) <= 100:
    save_by_key(get_train_tracker_trip_ids_key(tracker_id), trips)
    save_by_key(get_train_tracker_trip_ids_deviation_seconds_key(tracker_id), time_deviation_in_seconds)
  
        
def update_stop_time(tracker_id, prev_stop_id, arrival_unix_timestamp, stop_id_and_departure_time):
    prev_stops_counter_key = get_train_tracker_tracked_stops_prev_stops_counter_key(tracker_id)
    done = False
    while not done:
        p.watch(prev_stops_counter_key)
        prev_stops_counter_value = cl.get(prev_stops_counter_key)
        if prev_stops_counter_value is None or int(prev_stops_counter_value) < prev_stop_id:
            try:
                p.multi()
                p.zremrangebyscore(get_train_tracker_tracked_stops_key(tracker_id), arrival_unix_timestamp, arrival_unix_timestamp)
                p.zadd(get_train_tracker_tracked_stops_key(tracker_id), arrival_unix_timestamp, stop_id_and_departure_time)
                p.set(prev_stops_counter_key, prev_stop_id)
                res = p.execute()
                done = True
            except WatchError:
                done = False
                p.unwatch()
        else:
            done = True
            # Eran: I want to abort the watch. Should I use unwatch or discard? p.discard does not exist
            p.unwatch()
            

def add_prev_stop(tracker_id, stop_id, timestamp):
    next_id = cl.incr(get_train_tracker_prev_stops_counter_key(tracker_id))
    #p = get_redis_pipeline()
    #p.set("train_tracker:%s:%d:stop_id:" % (tracker_id, next_id), stop_id)
    unix_timestamp = ot_utils.dt_time_to_unix_time(timestamp)
    p.zadd(get_train_tracker_timestamp_sorted_stop_ids_key(tracker_id), unix_timestamp, "%d_%s" % (next_id, stop_id))
    p.zremrangebyrank(get_train_tracker_timestamp_sorted_stop_ids_key(tracker_id), 0, -HISTORY_LENGTH-1)
    p.execute()
    #p.set("train_tracker:%s:%d:timestamp:" % (tracker_id, next_id), timestamp)
    #p.execute()
    return next_id
            
        
        # grouping stop sequence snippet, not sure if iterator is right approach:
        #from itertools import groupby  
        #groups = groupby(zip(state_sequence, self.prev_stops_timestamps), lambda x: x[0])
        #stop_times = []
        #for stop_id,g in groups:
            #if stop_id != self.non_stop_component_num:
                #stop_time = TrackedStopTime(stop_id)
                #stop_times.append(stop_time)
                #stop_time.arrival = g.next()
                #for x in g:
                    #stop_time.departure = x

# None means we cannot find a reasonable trip list
# empty list means there are no trips that fit this tracker
def get_possible_trips(tracker_id, print_debug_info=False):
    stop_times_redis = cl.zrange(get_train_tracker_tracked_stops_key(tracker_id), 0, -1, withscores=True)
    if len(stop_times_redis) == 0:
        return None
    #arrival = get_localtime(datetime.datetime.fromtimestamp(stop_times_redis[0][1]), self.db_timezone)
    
    #shape_matches_inds = self.get_shape_ids_with_high_probability()

    #trips = gtfs.models.Trip.objects.filter(shape_id__in=shape_matches_inds, service__in=relevant_service_ids)
    relevant_service_ids = load_by_key(get_train_tracker_relevant_services_key(tracker_id))
    trips = gtfs.models.Trip.objects.filter(service__in=relevant_service_ids)

    # filter by stop existence and its time frame:
    trips_filtered_by_stops_and_times = trips
    if print_debug_info:
        print len(trips_filtered_by_stops_and_times)
    stop_times = []
    for cur in stop_times_redis:
        arrival = ot_utils.unix_time_to_localtime(int(cur[1]))
        cur_0_split = cur[0].split('_')
        stop_id = cur_0_split[0]
        name = stops.all_stops[stop_id].name
        departure = ot_utils.unix_time_to_localtime(int(cur_0_split[1])) if cur_0_split[1] != '' else None
        stop_times.append(TrackedStopTime(stop_id))
        stop_times[-1].arrival = arrival
        stop_times[-1].departure = departure
        
        trip_stop_times = gtfs.models.StopTime.objects.filter(trip__in = trips_filtered_by_stops_and_times)
        arrival_time__greater_than = arrival-datetime.timedelta(seconds=config.late_arrival_max_seconds)
        arrival_time__less_than = arrival+datetime.timedelta(seconds=config.early_arrival_max_seconds)
        arrival_time__range = datetime_range_to_db_time(arrival_time__greater_than, arrival_time__less_than)

        if departure is not None:
            departure_time__greater_than = departure-datetime.timedelta(seconds=config.late_departure_max_seconds)
            departure_time__less_than = departure+datetime.timedelta(seconds=config.early_departure_max_seconds)
            departure_time__range = datetime_range_to_db_time(departure_time__greater_than, departure_time__less_than)
        
            trip_stop_times_for_specific_stop = trip_stop_times.filter(stop = stop_id, 
                                                                       arrival_time__range=arrival_time__range,
                                                                       departure_time__range=departure_time__range)
        
        else:
            trip_stop_times_for_specific_stop = trip_stop_times.filter(stop = stop_id, 
                                                                       arrival_time__range=arrival_time__range)                
            
        trips_filtered_by_stops_and_times = trip_stop_times_for_specific_stop.values_list('trip')

        if print_debug_info:
            print len(trips_filtered_by_stops_and_times)
    
    # filter by stop order:
    trip_in_right_direction = []
    for i, t in enumerate(trips_filtered_by_stops_and_times):
        trip_stop_times = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time').values_list('stop')
        trip_stop_times = [str(x[0]) for x in trip_stop_times]
        stop_inds_by_visit_order = [trip_stop_times.index(x) for x in [x.stop_id for x in stop_times]]
        if is_increasing(stop_inds_by_visit_order):
            trip_in_right_direction.append(i)
    
    trips_filtered_by_stops_and_times = [trips_filtered_by_stops_and_times[i][0] for i in trip_in_right_direction]
    
    arrival_delta_abs_sums_seconds = []
    #departure_delta_abs_sums = []
    for t in trips_filtered_by_stops_and_times:
        stop_times_redis = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time').values_list('stop', 'arrival_time')#, 'departure_time')
        arrival_delta_abs_sum = 0
        #departure_delta_abs_sum = 0
        for tracked_stop_time in stop_times:
            stop_time = [x for x in stop_times_redis if str(x[0]) == tracked_stop_time.stop_id][0]
            arrival_delta_seconds = stop_time[1] - datetime_to_db_time(tracked_stop_time.arrival)
            #departure_delta_seconds = stop_time[2] - datetime_to_db_time(tracked_stop_time.departure)
            arrival_delta_abs_sum += abs(arrival_delta_seconds)
            #departure_delta_abs_sum += abs(departure_delta_seconds)
        arrival_delta_abs_sums_seconds.append(arrival_delta_abs_sum)
        #departure_delta_abs_sums.append(departure_delta_abs_sum)
    
    # sort results by increasing arrival time 
    sorted_trips = sorted(zip(arrival_delta_abs_sums_seconds,trips_filtered_by_stops_and_times))
    trips_filtered_by_stops_and_times = [x for (y,x) in sorted_trips]
    arrival_delta_abs_sums_seconds = [y for (y,x) in sorted_trips]
    return trips_filtered_by_stops_and_times, arrival_delta_abs_sums_seconds

def get_shape_probs(tracker_id):
    p.zrange(get_train_tracker_counters_key(tracker_id), 0, -1, withscores=True)
    p.get(get_train_tracker_total_key(tracker_id))
    res = p.execute()
    
    # need to take shape_counts, shape_counts from res
    return shape_counts/float(max(shape_counts))

def get_shape_ids_with_high_probability(tracker_id):
    shape_int_ids = np.where(get_shape_probs(tracker_id) >= config.shape_probability_threshold)[0]
    shape_ids = [shapes.all_shapes[x].id for x in shape_int_ids]
    return shape_ids

def print_possible_trips(tracker_id):
    trips = get_possible_trips(tracker_id)
    print 'Trip count = %d' %(len(trips))
    for t in trips:
        trip_stop_times = gtfs.models.StopTime.objects.filter(trip = t).order_by('arrival_time')
        print "trip id: %s" % (t)
        for x in trip_stop_times:
            print db_time_to_datetime(x.arrival_time), db_time_to_datetime(x.departure_time), x.stop
        print        
        
def print_tracked_stop_times(tracker_id):
    #for tracked_stop_time in self.stop_times:
    #    print tracked_stop_time
    res = cl.zrange(get_train_tracker_tracked_stops_key(tracker_id), 0, -1, withscores=True)
    for cur in res:
        arrival = ot_utils.unix_time_to_localtime(int(cur[1]))
        cur_0_split = cur[0].split('_')
        name = stops.all_stops[cur_0_split[0]].name
        departure = ot_utils.unix_time_to_localtime(int(cur_0_split[1])) if cur_0_split[1] != '' else None
        print TrackedStopTime.get_str(arrival, departure, name)


def add_report(report):  
    bssid_tracker.tracker.add(report)
    add_report_to_tracker(report.device_id, report)

hmm, hmm_non_stop_component_num = setup_hmm()
tracker_states = enum(INITIAL='initial', NOSTOP='nostop', STOP='stop', UNKNOWN='unknown')
nostop_id = stops.all_stops.id_list[hmm_non_stop_component_num]

cl = get_redis_client()
p = get_redis_pipeline()