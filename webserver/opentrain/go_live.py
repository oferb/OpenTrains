#!/usr/bin/env python

"""
script to run device id as live
To invoke:

./go_live.py dev1 dev2 delay server
    dev1:     original device
    dev2:     new fake device
    delay:    delay between each report
    server:   what server to use.
              if run locally use localhost:8000 if on real server use 192.241.154.128
              
    For example:  ./go_live.py 1cb87f1e eran1234 2 localhost:8000

"""


import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
import sys
import json
import time
import requests


def copy_reports(device_id):
    import reports.logic
    import common.ot_utils
    filename = os.path.join('/tmp/','reports_%s.txt' % common.ot_utils.get_local_time_underscored())
    reports.logic.copy_device_reports(device_id,filename)
    return filename

def report_fake(filename,dev2,delay,server):
    print 'In report fake:'
    print 'filename = %s' % (filename)
    print 'new device = %s' % (dev2)
    print 'delay = %f' % (delay)
    print 'server = %s' % (server) 
    
    with open(filename,'r') as fh:
        index = 0
        for line in fh:
            report = json.loads(line)
            items = report['items']
            for item in items:
                item['device_id'] = dev2 # replace device_id
                item['time'] = time.time() * 1000
                if item['location_api']:
                    item['location_api']['time'] = time.time() * 1000
                time.sleep(delay)
            body = json.dumps(report)
            headers = {'content-type':'application/json'}
            url = 'http://%s/reports/add/' % (server)
            resp = requests.post(url,headers=headers,data=body)
            if resp.status_code >= 400:
                print 'failed with: ' + resp.content
                with open('/tmp/error.html') as fh:
                    fh.write(resp.content)
            print 'Sent %d raw reports so far' % (index) 
            index += 1
            
def main(dev1,dev2,delay,server):
    filename = copy_reports(dev1)
    report_fake(filename,dev2,delay,server)
    
     
if __name__ == '__main__':
    if len(sys.argv) != 5:
        m = sys.modules[__name__]
        print m.__doc__
        sys.exit(255)
    main(sys.argv[1],sys.argv[2],float(sys.argv[3]),sys.argv[4])
