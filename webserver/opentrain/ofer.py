""" comment 
export DJANGO_SETTINGS_MODULE="opentrain.settings"
"""

import gtfs.models

def print_all(route_id):
    results = gtfs.models.Trip.objects.filter(route_id=route_id)
    for result in results:
        print result.trip_id

print_all(52)


