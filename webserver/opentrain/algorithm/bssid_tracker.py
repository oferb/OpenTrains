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
from redis_intf.client import get_redis_pipeline, get_redis_client

from export_utils import *

class BSSIDTracker(object):
    def __init__(self) :
        self.wifis_near_no_station = deque(maxlen=100) # limit size to avoid server memory issues
        self.wifis_near_two_or_more_stations = deque(maxlen=100) 
    
    def add(self, report):
        if not report.get_my_loc() or report.loc_ts_delta() > config.stop_discovery_location_timeout_seconds:
            return
        loc = report.get_my_loc()
        wifis = [x for x in report.get_wifi_set_all() if x.SSID == 'S-ISRAEL-RAILWAYS']
        if len(wifis) > 0:
            coords = [loc.lat, loc.lon]
            stop_id_list = stops.all_stops.query_stops(coords, meter_distance_to_coord_distance(config.station_radius_in_meters))
        
        for wifi in wifis:
            if len(stop_id_list) == 1:                
                p = get_redis_pipeline()
                stop_id = stops.all_stops[stop_id_list[0]].id
                p.zincrby("bssid:%s:counters" % (wifi.key), stop_id, 1)
                p.incr("bssid:%s:total" % (wifi.key))
                p.execute()                
            else:
                if len(stop_id_list) == 0:
                    self.wifis_near_no_station.append(wifi)
                else:
                    self.wifis_near_two_or_more_stations.append(wifi)

    def get_stop_id(self, bssid):
        p = get_redis_pipeline()
        p.zrange("bssid:%s:counters" % (bssid), -1, -1, withscores=True)
        p.get("bssid:%s:total" % (bssid))
        res = p.execute()
        
        stop_id, score = res[0][0]
        total = res[1]
        stop_probability = float(score)/float(total)

        return stop_id, stop_probability, total
    
    def has_bssid(self, bssid):
        cl = get_redis_client()
        return cl.exists("bssid:%s:total" % (bssid))
    
    def has_bssid_high_confidence(self, bssid):
        if not self.has_bssid(bssid):
            return False
        
        _, stop_probability, total = self.get_stop_id(bssid)
        if total < config.stop_discovery_count_thresh:
            return False

        if stop_probability < config.stop_discovery_probability_thresh:
            return False
        
        return True
             
    def print_table(self, bssids=None):
        print 'bssid\tcount\tprobability\tname' 
        if bssids is None:
            cl = get_redis_client()
            bssid_keys = cl.keys(pattern='bssid*total')
            bssids = [x.split(":")[1] for x in bssid_keys]
        
        for bssid in bssids:
            stop_id, stop_probability, total = self.get_stop_id(bssid)
            print '%s\t%s\t%.2f\t%s' % (bssid, total, stop_probability, stops.all_stops[stop_id].name)
       

def calc_tracker():
    cl = get_redis_client()
    keys = cl.keys(pattern='bssid*')
    if len(keys) > 0:
        cl.delete(*keys)
    tracker = BSSIDTracker()
    reports = analysis.models.Report.objects.filter(wifi_set__SSID = 'S-ISRAEL-RAILWAYS', my_loc__isnull=False).order_by('id')
    reports.prefetch_related('wifi_set', 'my_loc')
    # TODO: ask Eran is there's a better way to get unique reports (some kind of django join?):
    reports = list(set(reports))
    
    for report in reports:
        tracker.add(report)
    tracker.print_table()
    
    return tracker
    
def get_tracker(reset=False):
    if reset:
        bssid_tracker = calc_tracker()
    else:
        bssid_tracker = BSSIDTracker()
    
    return bssid_tracker

tracker = get_tracker(False)