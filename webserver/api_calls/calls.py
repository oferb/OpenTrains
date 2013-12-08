import requests
import urlparse
import json
import sys
import time

SERVER = 'http://localhost:8000/'
ERROR_FILE_NAME = '/tmp/error.html'

def call_and_check(func,url,*args,**kwargs):
    if not url.startswith('http'):
        url = urlparse.urljoin(SERVER,url)
    resp = func(url,*args,**kwargs)
    if (resp.status_code >= 400):
        fh = open(ERROR_FILE_NAME,'w')
        fh.write(resp.content)
        fh.close()
        raise Exception("Failed in %s for url = %s\nError file in file://%s" % (func.__name__,url,ERROR_FILE_NAME)) 
    else:
        return resp


def post_and_check(url,*args,**kwargs):
    func = requests.post
    return call_and_check(func,url,*args,**kwargs)

def post_and_check_json(*args,**kwargs):
    kwargs['headers'] = {'content-type' : 'application/json'}
    return post_and_check(*args,**kwargs)
    
def download_csv():
    post_and_check('/gtfs/download/')
    
def create_models():
    post_and_check('/gtfs/create-models/')

def create_superuser():
    post_and_check('/gtfs/create-superuser/')

def add_report():
    post_and_check_json('/reports/add/',data=json.dumps(dict(user='eran',wifis=[dict(loc="loc1",name="hello1"),
                                                                     dict(loc="loc2",name="hello2")])))


if __name__ == '__main__':
    for arg in sys.argv[1:]:
        print 'Doing %s' % (arg)
        m = globals()[arg]
        start_time = time.time()
        m()
        end_time = time.time()
        print('\ttook %.2f seconds' % (end_time - start_time))


        

