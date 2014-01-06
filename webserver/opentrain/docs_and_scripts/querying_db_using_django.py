""" comment 
export DJANGO_SETTINGS_MODULE="opentrain.settings"
"""

import gtfs.models

def print_all(route_id):
    results = gtfs.models.Trip.objects.filter(route_id=route_id)
    for result in results:
        print result.trip_id

print_all(52)

import analysis.models

def print_device_id(device_id):
    results = analysis.models.Report.objects.filter(device_id=device_id)
    for result in results:
        print result.timestamp

print_device_id("aaa")

def print_all_devices():
    results = analysis.models.Report.objects.all().values_list('device_id')
    for result in results:
        print result


def print_device_wifis(device_id):
    results = analysis.models.Report.objects.all()
    for result in results:
        print result, result.wifi_set.all()


print_device_id("aaa")
print_all_devices("aaa")
print_device_wifis("aaa")

