import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
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
from common.ot_utils import meter_distance_to_coord_distance

from export_utils import *

class BSSIDTracker(object):
    def __init__(self) :
        self.bssid_prob_map = {}
        self.bssid_counts_map = {}
        self.wifis_near_no_station = deque(maxlen=100) # limit size to avoid server memory issues
        self.wifis_near_two_or_more_stations = deque(maxlen=100)
    
    def add(self, report):
        if report.loc_ts_delta() < config.stop_discovery_location_timeout_seconds:
            pass
        
        coords = [report.my_loc.lat, report.my_loc.lon]
        stop_int_id_list = stops.all_stops.query_stops(coords, meter_distance_to_coord_distance(config.station_radius_in_meters))
        wifis = [x for x in report.wifi_set.all() if x.SSID == 'S-ISRAEL-RAILWAYS']
        for wifi in wifis:
            if len(stop_int_id_list) == 1:
                if not self.bssid_prob_map.has_key(wifi.key):
                    self.bssid_prob_map[wifi.key] = np.zeros(len(stops.all_stops))
                    self.bssid_counts_map[wifi.key] = 0
                self.bssid_prob_map[wifi.key][stop_int_id_list[0]] += 1
                self.bssid_counts_map[wifi.key] += 1
            else:
                if len(stop_int_id_list) == 0:
                    self.wifis_near_no_station.append(wifi)
                else:
                    self.wifis_near_two_or_more_stations.append(wifi)

    def get_stop_int_id(self, bssid):
        stop_int_id = np.argmax(self.bssid_prob_map[bssid])
        stop_probability = self.bssid_prob_map[bssid][stop_int_id]/self.bssid_counts_map[bssid]
        return stop_int_id, stop_probability
    
    def has_bssid(self, bssid):
        return self.bssid_prob_map.has_key(bssid)
    
    def has_bssid_high_confidence(self, bssid):
        if not self.bssid_prob_map.has_key(bssid):
            return False
        
        if self.bssid_counts_map[bssid] < config.stop_discovery_count_thresh:
            return False
        stop_int_id, stop_probability = self.get_stop_int_id(bssid)

        if stop_probability < config.stop_discovery_probability_thresh:
            return False
        
        return True
             
    def print_table(self):
        print 'bssid\tcount\tprobability\tname'    
        for bssid in self.bssid_prob_map.keys():
            stop_int_id, stop_probability = self.get_stop_int_id(bssid)
            print '%s\t%d\t%.2f\t%s' % (bssid, self.bssid_counts_map[bssid], stop_probability, stops.all_stops[stop_int_id].name)
       

def calc_tracker():
    tracker = BSSIDTracker()
    reports = analysis.models.Report.objects.filter(wifi_set__SSID = 'S-ISRAEL-RAILWAYS').order_by('id')
    reports.prefetch_related('wifi_set', 'my_loc')
    # TODO: ask Eran is there's a better way to get unique reports (some kind of django join?):
    reports = list(set(reports))
    
    for report in reports:
        tracker.add(report)
    tracker.print_table()
    
    return tracker
    
def get_tracker(reset=False):
    datafile = shelve.open(config.output_shelve_file)

    if not datafile.has_key('bssid_tracker') or reset:
        bssid_tracker = calc_tracker()
        datafile['bssid_tracker'] = bssid_tracker
    bssid_tracker = datafile['bssid_tracker']
    
    datafile.close() 
    
    return bssid_tracker

def save_tracker(tracker):
    datafile = shelve.open(config.output_shelve_file)
    datafile['bssid_tracker'] = tracker
    datafile.close() 

tracker = get_tracker()