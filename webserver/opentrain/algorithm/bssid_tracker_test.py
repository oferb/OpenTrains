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

from display_utils import *
from export_utils import *
import shapes
from train_tracker import TrainTracker

from analysis.models import SingleWifiReport
import bssid_tracker

class BSSIDTrackerTest(TestCase):

    def setUp(self):
        self.stop_bssids = analysis.models.SingleWifiReport.objects.filter(SSID = 'S-ISRAEL-RAILWAYS').values('key').distinct()
        self.stop_bssids = [x['key'] for x in self.stop_bssids]              
        
    def test_all_mappings_pass_threshold(self):
        bssids = [x for x in self.stop_bssids if bssid_tracker.tracker.has_bssid(x)]
        low_confidence_bssids = [x for x in bssids if bssid_tracker.tracker.get_stop_int_id(x)[1] < config.stop_discovery_probability_thresh]
        
        self.assertEquals(len(low_confidence_bssids), 0)

    def test_all_bssids_are_mapped(self):
        unmapped_bssids = [x for x in self.stop_bssids if not bssid_tracker.tracker.has_bssid(x)]
        
        self.assertEquals(len(unmapped_bssids),0, '%s bssids are not mapped' % (unmapped_bssids))
    
        
if __name__ == '__main__':
    unittest.main()