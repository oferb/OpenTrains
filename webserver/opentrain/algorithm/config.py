import config 
import os

def set_config(base_dir):
    config.base = base_dir
    config.temp_data = os.path.join(config.base, 'tmp_data')
    
    # data folders
    config.gtfs = os.path.join(config.temp_data, 'gtfs')
    config.gtfs_raw_data = os.path.join(config.gtfs, 'data')
    config.gtfs_processed_data = os.path.join(config.gtfs, 'processed_data')
    
    # output folders
    config.output_data = os.path.join(config.temp_data, 'output')    

    # params
    config.max_accuracy_radius_meters = 300
    config.min_accuracy_radius_meters = 200
    config.route_sampling__min_distance_between_points_meters = 10.0
    config.station_radius_in_meters = 300
    config.early_arrival_max_seconds = 45 * 60 # how early can a train arrive before the actual arrival
    config.late_arrival_max_seconds = 45 * 60 # how late can a train arrive before the actual arrival
    config.early_departure_max_seconds = 10 * 60 # how early can a train depart before the actual departure
    config.late_departure_max_seconds = 45 * 60 # how late can a train depart before the actual departure
    config.shape_probability_threshold= 0.8
    
base_dir = os.path.dirname(os.path.dirname(__file__))
set_config(base_dir)