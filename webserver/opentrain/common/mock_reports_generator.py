""" comment 
export DJANGO_SETTINGS_MODULE="opentrain.settings"
"""
import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
#/home/oferb/docs/train_project/OpenTrains/webserver
import gtfs.models
import analysis.models
import numpy as np
import itertools
import datetime
import algorithm.shapes as shapes
import algorithm.stops as stops
import ot_utils

def generate_mock_reports(device_id='fake_device_1', trip_id='260214_00077', day=None, from_stop_id=None, to_stop_id=None, nostop_percent=0.2, station_radius_in_meters=300):
    trips = gtfs.models.Trip.objects.filter(trip_id=trip_id)
    trip = trips[0]
    shape_points = gtfs.models.Shape.objects.filter(shape_id=trip.shape_id).order_by('shape_pt_sequence')
    stop_times = gtfs.models.StopTime.objects.filter(trip=trip_id).order_by('arrival_time')
    if not day:
        day = ot_utils.get_localtime_now()
    
    # filter stop times by from_stop_id and to_stop_id:
    trip_stop_ids = [str(x.stop.stop_id) for x in stop_times]
    from_stop_ind = 0
    if from_stop_id:
        from_stop_ind = trip_stop_ids.index(from_stop_id)
    to_stop_ind = None
    if to_stop_id:
        to_stop_ind = trip_stop_ids.index(to_stop_id)+1
    stop_times = stop_times[from_stop_ind:to_stop_ind]
    trip_stop_ids = set([str(x.stop.stop_id) for x in stop_times])

    # get coords:
    coords = []
    for x in shape_points:
        coords.append([x.shape_pt_lat, x.shape_pt_lon])
    coords = np.array(coords)
    accuracies = np.ones((len(coords),1))*ot_utils.meter_distance_to_coord_distance(station_radius_in_meters)
    
    # map shape-points to stops:
    stop_ids = stops.all_stops.query_stops(coords, accuracies)
    
    # filter out stops not in trip:
    stop_ids_uniques = set(stop_ids)
    if len(trip_stop_ids - stop_ids_uniques) > 0:
        unfound_stops = trip_stop_ids - stop_ids_uniques
        print('Warning: these stops were not found in gtfs shape: %s' % (unfound_stops))
    stops_not_in_trip = stop_ids_uniques - trip_stop_ids - set([stops.NOSTOP])
    stop_ids = [x if x not in stops_not_in_trip else stops.NOSTOP for x in stop_ids]

    # strip nostops from start and end
    while len(stop_ids) > 0 and stop_ids[0] == stops.NOSTOP:
        del stop_ids[0]
    while len(stop_ids) > 0 and stop_ids[-1] == stops.NOSTOP:
        del stop_ids[-1]    

    # remove nostop reports according to nostop_percent:
    nostop_inds = [i for i in xrange(len(stop_ids)) if stop_ids[i] == stops.NOSTOP]
    keep_inds = [i for i in xrange(len(stop_ids)) if stop_ids[i] != stops.NOSTOP]
    nostop_inds = nostop_inds[::int(1/nostop_percent)]
    keep_inds.extend(nostop_inds)
    stop_ids = [stop_ids[i] for i in xrange(len(stop_ids)) if i in keep_inds]
    shape_points = [shape_points[i] for i in xrange(len(shape_points)) if i in keep_inds]


    stop_id_to_stop_time_dict = {}
    for stop_time in stop_times:
        stop_id_to_stop_time_dict[str(stop_time.stop.stop_id)] = stop_time
    
    from itertools import groupby
    stop_id_groups = []
    stop_id_group_lens = []
    stop_id_unique_keys = []
    for k, g in groupby(stop_ids):
        g = list(g)
        stop_id_groups.append(g)      # Store group iterator as a list
        stop_id_group_lens.append(len(g))
        stop_id_unique_keys.append(k)     

    # create reports with corresponding location and wifi:
    reports = []
    last_stop = None
    prev_stop_id = None
    stop_index = -1
    counter = -1
    for shape_point, stop_id, i in zip(shape_points, stop_ids, xrange(len(stop_ids))):
        if stop_id != prev_stop_id:
            counter = -1
            if stop_id != stops.NOSTOP:
                stop_index += 1
                interval_start = stop_times[stop_index].arrival_time
                interval_end = stop_times[stop_index].departure_time
                #print '%s %s' % (stop_id, stop_times[stop_index].stop.stop_id)
            else:
                interval_start = stop_times[stop_index].departure_time
                interval_end = stop_times[stop_index+1].arrival_time
        #print i, stop_id       
        counter += 1
        interval_ratio = float(counter)/stop_id_group_lens[stop_index]
        timestamp = int(interval_start + interval_ratio*(interval_end-interval_start))
        timestamp = day.replace(hour=timestamp/3600, minute=timestamp % 3600 / 60, second=timestamp % 60 / 60)
        
        report = analysis.models.Report()
        reports.append(report)
        loc = analysis.models.LocationInfo()
        loc.report = report
        loc.accuracy = 0.1
        loc.lat = shape_point.shape_pt_lat
        loc.lon = shape_point.shape_pt_lon
        loc.provider = 'mock'
        loc.timestamp = timestamp
        report.my_loc_mock = loc
        
        wifi_report_train = analysis.models.SingleWifiReport()
        wifi_report_train.report = report
        wifi_report_train.SSID = TRAIN_SSID
        wifi_report_train.key = 'fake_bssid_train__%s' % (device_id)    
        report.wifi_set_mock = [wifi_report_train]
    
        if stop_id != stops.NOSTOP:
            wifi_report_station = analysis.models.SingleWifiReport()
            wifi_report_station.report = report
            wifi_report_station.SSID = STATION_SSID
            wifi_report_station.key = 'fake_bssid_stop__%s' % (stop_id)
            report.wifi_set_mock.append(wifi_report_station)
        
        report.device_id = device_id
        report.timestamp = timestamp
        report.created = timestamp
        
        report.device_id = device_id
        
        prev_stop_id = stop_id
    
    return reports

#general
STATION_SSID = 'S-ISRAEL-RAILWAYS'
TRAIN_SSID = 'ISRAEL-RAILWAYS'

if __name__ == '__main__':
    reports = generate_mock_reports(nostop_percent=0.05)
    print len(reports)