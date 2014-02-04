#!/usr/bin/env python

import requests
import argparse

def cache_date(year,month,day,server):
    print 'Caching for %s/%s/%s on %s' % (day,month,year,server)
    trip_ids = requests.get('http://%s/gtfs/trips-for-date' % (server),params=dict(year=year,month=month,day=day)).json()
    print 'Found %s trip ids for %s/%s/%s' % (len(trip_ids),day,month,year)
    bad = []
    for idx,trip_id in enumerate(trip_ids):
        url = 'http://%s/api/v1/trips/%s/' % (server,trip_id)
        resp = requests.get(url)
        if resp.status_code >= 400:
            print 'failed for trip_id %s' % (trip_id)
            bad.append(trip_id)
        else:
            print '%d (from %d) succeed for trip_id %s' % (idx,len(trip_ids),trip_id)
    print 'Summary: total = %s bad = %d' % (len(trip_ids),len(bad))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='cache trips for date')
    parser.add_argument('--year',help='year',required=True)
    parser.add_argument('--month',help='month',required=True)
    parser.add_argument('--day',help='day',required=True)
    parser.add_argument('--server',help='server',default='localhost:8000',required=False)
    ns = parser.parse_args()
    cache_date(year=ns.year,month=ns.month,day=ns.day,server=ns.server)

