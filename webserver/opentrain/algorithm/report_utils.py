import gtfs.models
import analysis.models
import numpy as np
from scipy import spatial
import shelve
import matplotlib.pyplot as plt
import simplekml
import config
import itertools
import os

from geo_utils import *

def get_location_info_from_device_id(device_id):
    locations = analysis.models.LocationInfo.objects.filter(report__device_id=device_id).order_by('timestamp')
    lat_list = [float(x[0]) for x in list(locations.all().values_list('lat'))]
    lon_list = [float(x[0]) for x in list(locations.all().values_list('lon'))]
    device_accuracies_in_meters = [float(x[0]) for x in list(locations.all().values_list('accuracy'))]
    device_timestamps = [x[0] for x in list(locations.all().values_list('timestamp'))]
    device_accuracies_in_meters = np.array(device_accuracies_in_meters)
    device_accuracies_in_meters[device_accuracies_in_meters > config.max_accuracy_radius_meters] = config.max_accuracy_radius_meters
    device_accuracies_in_meters[device_accuracies_in_meters < config.min_accuracy_radius_meters] = config.min_accuracy_radius_meters

    device_coords = zip(lat_list, lon_list)
    device_coords = np.array(device_coords)
    device_accuracies_in_coords = [meter_distance_to_coord_distance(x) for x in device_accuracies_in_meters]
    return device_coords, device_timestamps, device_accuracies_in_meters, device_accuracies_in_coords