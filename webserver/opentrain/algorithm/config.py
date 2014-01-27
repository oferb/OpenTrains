import config 
import os
from common.ot_utils import mkdir_p

def set_config(base_dir):
    config.base = base_dir
    config.temp_data = os.path.join(config.base, 'tmp_data')
    
    # gtfs
    config.gtfs = os.path.join(config.temp_data, 'gtfs')
    config.gtfs_raw_data = os.path.join(config.gtfs, 'data')
    config.gtfs_processed_data = os.path.join(config.gtfs, 'processed_data')
    mkdir_p(config.gtfs_processed_data)
    config.gtfs_shelve_file = os.path.join(config.gtfs_processed_data, 'shelve.data') 
    
    # reports
    config.output_data = os.path.join(config.temp_data, 'output')  
    mkdir_p(config.output_data)    
    config.output_shelve_file = os.path.join(config.output_data, 'shelve.data')  

    # params
    config.max_accuracy_radius_meters = 300
    config.min_accuracy_radius_meters = 200
    config.route_sampling__min_distance_between_points_meters = 10.0
    config.station_radius_in_meters = 300
    config.early_arrival_max_seconds = 45 * 60 # how early can a train arrive before the actual arrival
    config.late_arrival_max_seconds = 45 * 60 # how late can a train arrive before the actual arrival
    config.early_departure_max_seconds = 15 * 60 # how early can a train depart before the actual departure
    config.late_departure_max_seconds = 45 * 60 # how late can a train depart before the actual departure
    config.shape_probability_threshold= 0.80
    config.stop_discovery_location_timeout_seconds = 60
    config.stop_discovery_probability_thresh = 0.95
    config.stop_discovery_count_thresh = 10
    
base_dir = os.path.dirname(os.path.dirname(__file__))
set_config(base_dir)