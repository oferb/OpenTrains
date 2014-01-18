from unittest import TestCase
import unittest
from alg_utils import *


class gtfs_test(TestCase):
    
    def setUp(self):
        shape_int_ids, unique_shape_ids, shape_point_tree, sampled_all_routes_tree, stop_ids, stop_point_tree, stop_names = load_gtfs_data()
        
        # TODO: Ask Udi how to not have to use self everywhere (class/instance) methods
        # TODO: Ask Udi how to get nose to work (ImportError: No module named gtfs.models)
        self.shape_int_ids = shape_int_ids
        self.unique_shape_ids = unique_shape_ids
        self.shape_point_tree = shape_point_tree
        self.sampled_all_routes_tree = sampled_all_routes_tree
        self.stop_ids = stop_ids
        self.stop_point_tree = stop_point_tree
        self.stop_names = stop_names
       
    
    def get_trips(self, device_id):
        trips_filtered_by_stops_and_times = match_device_id(device_id, self.sampled_all_routes_tree, self.shape_point_tree, self.shape_int_ids, self.unique_shape_ids, self.stop_point_tree, self.stop_ids, self.stop_names)
        return trips_filtered_by_stops_and_times
        
    
    def test_matches(self):

        device_id = '02090d12' # Eran's trip
        trips = self.get_trips(device_id)
        self.assertTrue(len(trips) == 3)
        self.assertTrue('130114_00177' in trips)
        self.assertTrue('130114_00175' in trips)
        self.assertTrue('130114_00077' in trips)
        
        device_id = 'f752c40d' # Ofer's trip
        trips = self.get_trips(device_id)
        self.assertTrue(len(trips) == 1)        
        self.assertTrue('130114_00283' in trips)
    
        device_id = '1cb87f1e' # Udi's trip        
        trips = self.get_trips(device_id)
        self.assertTrue(len(trips) == 2)        
        self.assertTrue('160114_00171' in trips)
        self.assertTrue('160114_00073' in trips)
        

    
if __name__ == '__main__':
    unittest.main()