#!/usr/bin/env python
import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
import sys
import gtfs.models

trips = gtfs.models.Trip.objects.filter(trip_id=sys.argv[1])
print('')
trips[0].print_stoptimes()
print('')
