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
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass
import simplekml
import config
import itertools
import datetime
from unittest import TestCase
import unittest
import time
from display_utils import *
from export_utils import *
import shapes

import stops
from train_tracker import TrainTracker

from analysis.models import SingleWifiReport
from redis_intf.client import get_redis_pipeline, get_redis_client

class train_tracker_test(TestCase):
    
    def track_device(self, device_id, do_print=False, do_preload_reports=True):
        #device_coords, device_timestamps, device_accuracies_in_meters, device_accuracies_in_coords = get_location_info_from_device_id(device_id)
        reports_queryset = self.get_data_from_device_id(device_id)
        
        tracker = TrainTracker(device_id)
        
        fps_period_start = time.clock()
        fps_period_length = 100
        if do_preload_reports:
            reports_queryset = list(reports_queryset)
        count = len(reports_queryset) if isinstance(reports_queryset, list) else reports_queryset.count()
        for i in xrange(count):
            if i % fps_period_length == 0:
                elapsed = (time.clock() - fps_period_start)
                if elapsed > 0:
                    print('%d\t%.1f qps' % (i, fps_period_length/elapsed))
                else:
                    print('Elapsed time should be positive but is %d' % (elapsed))
                fps_period_start = time.clock()                
            
            if i % 900 == 0:
                trips = tracker.get_possible_trips()
            report = reports_queryset[i]
            
            tracker.add(report)
            

        #tracker.print_tracked_stop_times()
        #tracker.print_possible_trips()
        trips, deviation_in_seconds = tracker.get_possible_trips()
        return trips, tracker
        
  
    def test_tracker_on_devices(self):
        cl = get_redis_client()
        keys = cl.keys(pattern='train_tracker:*')
        if len(keys) > 0:
            cl.delete(*keys)

        device_id = '02090d12' # Eran's trip
        trips, tracker = self.track_device(device_id, do_preload_reports=True)
        print trips
        self.assertEquals(len(trips), 2)
        self.assertTrue('130114_00077' in trips)
        self.assertTrue('130114_00177' in trips)
        
        device_id = 'f752c40d' # Ofer's trip
        trips, tracker = self.track_device(device_id)
        print trips
        self.assertEquals(len(trips), 1)        
        self.assertTrue('130114_00283' in trips)
        tracker.print_possible_trips()
        
        device_id = '1cb87f1e' # Udi's trip        
        trips, tracker = self.track_device(device_id)
        print trips
        self.assertEquals(len(trips), 1)        
        self.assertTrue('160114_00073' in trips)

    def get_data_from_device_id(self, device_id):
        qs = analysis.models.Report.objects.filter(device_id=device_id)#,my_loc__isnull=False)
        #qs = qs.filter(timestamp__day=device_date_day,timestamp__month=device_date_month,timestamp__year=device_date_year)
        qs = qs.order_by('timestamp')
        qs = qs.prefetch_related('wifi_set','my_loc')
        #reports = list(qs) takes a long time
        return qs    
        
if __name__ == '__main__':
    unittest.main()