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
from common import ot_utils
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass
import datetime
import bssid_tracker 
from redis_intf.client import get_redis_pipeline, get_redis_client

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
        
     
 
class TrainTracker(object):

    def __init__(self, id_) :
        self.id = id_
        #self.track_shape_int_ids = []
        #self.coords = []
        #self.visited_shape_point_ids = set()
        #self.shape_counts = np.zeros((len(shapes.all_shapes), 1))
        #self.current_stop_id = None
        cl = get_redis_client()
        cl.set("train_tracker:%s:current_stop_id" % (self.id), stops.NOSTOP)
        
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
        
        self.history_length = 1000
        #self.prev_stops = deque(maxlen=self.history_length)
        #self.prev_stops_timestamps = deque(maxlen=self.history_length)
        #self.stop_times = []
        
    def add(self, report):
        if not hasattr(self, 'relevant_service_ids'):
            start_date = report.timestamp.strftime("%Y-%m-%d")
            relevant_services = gtfs.models.Service.objects.filter(start_date = start_date)
            self.relevant_service_ids = relevant_services.all().values_list('service_id')
            
        
        # update train position
        coords = [report.my_loc.lat, report.my_loc.lon]
        res_shape_sampled_point_ids, _ = shapes.all_shapes.query_sampled_points(coords, report.my_loc.accuracy_in_coords)
        cl = get_redis_client()   
        added_count = cl.sadd("train_tracker:%s:visited_shape_sampled_point_ids" % (self.id), res_shape_sampled_point_ids)
        trips = cl.get("train_tracker:%s:trip_ids" % (self.id))
        trip = trips.split(',')[0] if trips is not None and len(trips) > 0 else None
        if added_count > 0:
            p = get_redis_pipeline()
            p.set("train_tracker:%s:coords" % (self.id), coords)
            
            if trip is not None:
                p.set('current_trip_id:coords:%s' % (trip), coords)
                p.set('current_trip_id:coords_timestamp:%s' % (trip), ot_utils.dt_time_to_unix_time(report.timestamp))
            p.execute()              
        
        if trip is not None:    
            cl.set('current_trip_id:report_timestamp:%s' % (trip), ot_utils.dt_time_to_unix_time(report.timestamp))
        
        #coords_updated = False
        #p = get_redis_pipeline()
        #p.zincrby("train_tracker:%s:counters" % (self.id), res_shape_ids[i], inc_by)
        #p.incr("train_tracker:%s:total" % (self.id), inc_by)
        #p.execute()        

        #for i in xrange(len(res_shape_point_ids)):
            #cl = get_redis_client()
            #if cl.sadd("train_tracker:%s:visited_shape_point_ids" % (self.id), res_shape_point_ids[i]) == 0:
                #if not coords_updated: #update if report adds new points on tracks
                    #self.coords = coords
                    #coords_updated = True
                #p = get_redis_pipeline()
                #p.zincrby("train_tracker:%s:counters" % (self.id), res_shape_ids[i], 1)
                #p.incr("train_tracker:%s:total" % (self.id))
                #p.execute()
                ##self.shape_counts[res_shape_ids[i]] = self.shape_counts[res_shape_ids[i]] + 1
        
        # 1) add stop or non-stop to prev_stops and prev_stops_timestamps     
        # 2) set calc_hmm to true if according to wifis and/or location, our state changed from stop to non-stop or vice versa
        calc_hmm = False
        prev_stop_id = None
        current_stop_id = cl.get("train_tracker:%s:current_stop_id" % (self.id))
        if report.is_station():
            wifis = [x for x in report.wifi_set.all() if x.SSID == 'S-ISRAEL-RAILWAYS']
            wifi_stops_ids = set()
            for wifi in wifis:
                if bssid_tracker.tracker.has_bssid_high_confidence(wifi.key):
                    stop_id ,_ ,_ = bssid_tracker.tracker.get_stop_id(wifi.key)
                    wifi_stops_ids.add(stop_id)
            
            wifi_stops_ids = np.array(list(wifi_stops_ids))

            
            # check all wifis show same station:
            if len(wifi_stops_ids) > 0 and np.all(wifi_stops_ids == wifi_stops_ids[0]):
                timestamp = report.get_timestamp_israel_time()
                stop_id = wifi_stops_ids[0]
                #self.prev_stops.append(stops.all_stops.id_list.index(stop_id))
                #self.prev_stops_timestamps.append(timestamp)
                prev_stop_id = self.add_prev_stop(stop_id, timestamp)
                
                if current_stop_id == stops.NOSTOP:
                    calc_hmm = True
            # comment explained in quotes: "in wifi we trust", "if they have no wifi let them use location"            
            elif report.loc_ts_delta() < config.stop_discovery_location_timeout_seconds:  
                
                coords = [report.my_loc.lat, report.my_loc.lon]
                stop_id_list = stops.all_stops.query_stops(coords, ot_utils.meter_distance_to_coord_distance(config.station_radius_in_meters))
                if len(stop_id_list) == 1:
                    timestamp = report.get_timestamp_israel_time()
                    stop_id = stop_id_list[0]                    
                    #self.prev_stops.append(stops.all_stops.id_list.index(stop_id))
                    #self.prev_stops_timestamps.append(timestamp)
                    prev_stop_id = self.add_prev_stop(stop_id, timestamp)
                    if current_stop_id == stops.NOSTOP:
                        calc_hmm = True
                    

        else:
            #self.prev_stops.append(self.non_stop_component_num)
            #self.prev_stops_timestamps.append(report.get_timestamp_israel_time())
            timestamp = report.get_timestamp_israel_time()
            stop_id = stops.all_stops.id_list[self.non_stop_component_num]
            prev_stop_id = self.add_prev_stop(stop_id, timestamp)
            if current_stop_id != stops.NOSTOP:
                calc_hmm = True
                
        # calculate hmm to get state_sequence, update stop_times and current_stop if needed
        if calc_hmm:
            p = get_redis_pipeline()
            p.zrange("train_tracker:%s:timestamp_sorted_stop_ids" % (self.id), 0, -1, withscores=True)
            p.get("train_tracker:%s:current_stop_id" % (self.id))
            res = p.execute()
            prev_stops = res[0]
            prev_current_stop = res[1]
            
            prev_stop_ids = [x[0] for x in prev_stops]
            prev_stop_int_ids = np.array([stops.all_stops.id_list.index(x.split("_")[1]) for x in prev_stop_ids])
            #assert np.array_equal(prev_stop_int_ids, np.array(self.prev_stops))
            logprob, state_sequence = self.hmm.decode(prev_stop_int_ids)
            self.state_sequence_for_debug = state_sequence
            
            current_stop_id = stops.all_stops.id_list[state_sequence[-1]]
            ##cl.set("train_tracker:%s:current_stop_id" % (self.id), current_stop_id)
            cl.set("train_tracker:%s:current_stop_id" % (self.id), current_stop_id)
            #if stops.all_stops.id_list[state_sequence[-1]] == self.non_stop_component_num:
                #current_stop_id = stops.NOSTOP
                #cl.set("train_tracker:%s:current_stop_id" % (self.id), current_stop_id)
                #self.current_stop_id = None
            #else:
                #current_stop_id = stops.all_stops.id_list[state_sequence[-1]]
                #cl.set("train_tracker:%s:current_stop_id" % (self.id), current_stop_id)
                #self.current_stop_id = stops.all_stops.id_list[state_sequence[-1]]
            
            prev_timestamp = None
            if prev_current_stop != current_stop_id:
                
                prev_stops_by_hmm = [stops.all_stops.id_list[x] for x in state_sequence]
                prev_stops_timestamps = [ot_utils.unix_time_to_localtime((x[1])) for x in prev_stops]
                for i, stop_id, timestamp in reversed(zip(range(len(prev_stops_by_hmm)), prev_stops_by_hmm, prev_stops_timestamps)):
                    #current_stop_component_num = stops.all_stops.ids_list.index(current_stop_id)
                    # test if this is where we changed states, or this is the first state
                    if (stop_id != current_stop_id or i == 0):
                        if current_stop_id == stops.NOSTOP: # we need to set departure
                            #self.stop_times[-1].departure = timestamp
                            stop_time = cl.zrange("train_tracker:%s:tracked_stops" % (self.id), -1, -1, withscores=True)
                            #arrival_unix_timestamp = ot_utils.dt_time_to_unix_time(self.stop_times[-1].arrival)
                            departure_unix_timestamp = ot_utils.dt_time_to_unix_time(timestamp)
                            stop_id_and_departure_time = "%s_%d" % (prev_current_stop, departure_unix_timestamp)
                            self.update_stop_time(prev_stop_id, stop_time[0][1], stop_id_and_departure_time)
                            self.update_trips(report, coords)
                        else: # we need to set arrival
                             # set new stop_time if no stop_time exists or on stop_id change
                            stop_time = cl.zrange("train_tracker:%s:tracked_stops" % (self.id), -1, -1, withscores=True)
                            if len(stop_time) == 0 or stop_time[0][0].split('_')[0] != current_stop_id:
                                arrival = prev_timestamp if prev_timestamp is not None else timestamp
                                arrival_unix_timestamp = ot_utils.dt_time_to_unix_time(arrival)
                                
                                stop_id_and_departure_time = "%s_" % (current_stop_id)
                                self.update_stop_time(prev_stop_id, arrival_unix_timestamp, stop_id_and_departure_time)
                                self.update_trips(report, coords)
                                
                                #stop_time = TrackedStopTime(current_stop_id)
                                #self.stop_times.append(stop_time)
                                #stop_time.arrival = prev_timestamp if prev_timestamp is not None else timestamp
                        break
                    prev_timestamp = timestamp
            self.print_tracked_stop_times()

    def update_trips(self, report, coords):
        trips, time_deviation_in_seconds = self.get_possible_trips()
        if len(trips) <= 3:
            cl = get_redis_client()
            cl.set("train_tracker:%s:trip_ids" % (self.id), ",".join(trips))
          
            
    def update_stop_time(self, prev_stop_id, arrival_unix_timestamp, stop_id_and_departure_time):
        p = get_redis_pipeline()
        cl = get_redis_client()
        prev_stops_counter_key = "train_tracker:%s:tracked_stops:prev_stops_counter" % (self.id)
        done = False
        while not done:
            p.watch(prev_stops_counter_key)
            prev_stops_counter_value = cl.get(prev_stops_counter_key)
            if prev_stops_counter_value is None or int(prev_stops_counter_value) < prev_stop_id:
                try:
                    p.multi()
                    p.zremrangebyscore("train_tracker:%s:tracked_stops" % (self.id), arrival_unix_timestamp, arrival_unix_timestamp)
                    p.zadd("train_tracker:%s:tracked_stops" % (self.id), arrival_unix_timestamp, stop_id_and_departure_time)
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
                
        

    def add_prev_stop(self, stop_id, timestamp):
        cl = get_redis_client()
        next_id = cl.incr("train_tracker:%s:prev_stops_counter" % (self.id))
        #p = get_redis_pipeline()
        #p.set("train_tracker:%s:%d:stop_id:" % (self.id, next_id), stop_id)
        unix_timestamp = ot_utils.dt_time_to_unix_time(timestamp)
        p = get_redis_pipeline()
        p.zadd("train_tracker:%s:timestamp_sorted_stop_ids" % (self.id), unix_timestamp, "%d_%s" % (next_id, stop_id))
        p.zremrangebyrank("train_tracker:%s:timestamp_sorted_stop_ids" % (self.id), 0, -self.history_length-1)
        p.execute()
        #p.set("train_tracker:%s:%d:timestamp:" % (self.id, next_id), timestamp)
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
    def get_possible_trips(self, print_debug_info=False):
        cl = get_redis_client()
        stop_times_redis = cl.zrange("train_tracker:%s:tracked_stops" % (self.id), 0, -1, withscores=True)
        if len(stop_times_redis) == 0:
            return None
        #arrival = get_localtime(datetime.datetime.fromtimestamp(stop_times_redis[0][1]), self.db_timezone)
        
        #shape_matches_inds = self.get_shape_ids_with_high_probability()

        #trips = gtfs.models.Trip.objects.filter(shape_id__in=shape_matches_inds, service__in=relevant_service_ids)
        trips = gtfs.models.Trip.objects.filter(service__in=self.relevant_service_ids)
    
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

     
    def get_shape_probs(self):
        p = get_redis_pipeline()
        p.zrange("train_tracker:%s:counters" % (self.id), 0, -1, withscores=True)
        p.get("train_tracker:%s:total" % (self.id))
        res = p.execute()
        
        return self.shape_counts/float(max(self.shape_counts))

    def get_shape_ids_with_high_probability(self):
        shape_int_ids = np.where(self.get_shape_probs() >= config.shape_probability_threshold)[0]
        shape_ids = [shapes.all_shapes[x].id for x in shape_int_ids]
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
        #for tracked_stop_time in self.stop_times:
        #    print tracked_stop_time
        cl = get_redis_client()
        res = cl.zrange("train_tracker:%s:tracked_stops" % (self.id), 0, -1, withscores=True)
        for cur in res:
            arrival = ot_utils.unix_time_to_localtime(int(cur[1]))
            cur_0_split = cur[0].split('_')
            name = stops.all_stops[cur_0_split[0]].name
            departure = ot_utils.unix_time_to_localtime(int(cur_0_split[1])) if cur_0_split[1] != '' else None
            print TrackedStopTime.get_str(arrival, departure, name)
 
trackers_by_device_id = {}
def add_report(report):  
    if not trackers_by_device_id.has_key(report.device_id):
        trackers_by_device_id[report.device_id] = TrainTracker(report.device_id)
    
    trackers_by_device_id[report.device_id].add(report)        

