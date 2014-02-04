#!/usr/bin/env python

import requests
import argparse
import datetime

def cache_date(date,today,server):
    params = dict()
    if today:
        params['today']=1
    else:
        params['date']=date
    resp = requests.get('http://%s/gtfs/api/trips-for-date/' % (server),params=params)    
    trip_ids = resp.json()['objects']
    assert len(trip_ids) == resp.json()['meta']['total_count']
    print 'Found %s trip ids for %s' % (len(trip_ids),('today' if today else date))
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--date',help='generate cache for specific date in format day/month/year',required=False)
    group.add_argument('--today',help='generate cache for today',required=False,action='store_true')
    parser.add_argument('--server',help='server',default='localhost:8000',required=False)
    
    ns = parser.parse_args()
    cache_date(date=ns.date,today=ns.today,server=ns.server)

