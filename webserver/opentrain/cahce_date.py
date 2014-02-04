#!/usr/bin/env python

import requests
import argparse

def cache_date(year,month,day,server):
    print 'Caching for %s/%s/%s on %s' % (day,month,year,server)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='cache trips for date')
    parser.add_argument('--year',help='year',required=True)
    parser.add_argument('--month',help='month',required=True)
    parser.add_argument('--day',help='day',required=True)
    parser.add_argument('--server',help='server',default='localhost:8000',required=False)
    ns = parser.parse_args()
    cache_date(year=ns.year,month=ns.month,day=ns.day,server=ns.server)

