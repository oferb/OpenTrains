import datetime
import zipfile
import os
import time
from django.conf import settings
from django.utils import timezone

def get_utc_time_underscored():
    """ return UTC time as underscored, to timestamp folders """
    t = datetime.datetime.utcnow()
    return t.strftime('%Y_%m_%d_%H_%M_%S')

def mkdir_p(path):
    """ mkdir -p path """
    if not os.path.exists(path):
        os.makedirs(path)
    
def ftp_get_file(host,remote_name,local_path):
    """ get file remote_name from FTP host host and copied it inot local_path"""
    from ftplib import FTP
    f = FTP(host)
    f.login()
    fh = open(local_path,'wb')
    f.retrbinary('RETR %s' % (remote_name), fh.write)
    fh.close()
    f.quit()
    print("Copied from host %s: %s => %s" % (host,remote_name,local_path))
    
    
def unzip_file(fname,dirname):
    """ unzip file fname into dirname """
    zf = zipfile.ZipFile(fname)
    zf.extractall(path=dirname)
    print("Unzipped %s => %s" % (fname,dirname))
    
        
def benchit(func):
    """ decorator to measure time """
    def wrap(*args,**kwargs):
        time_start = time.time()
        res = func(*args,**kwargs)
        time_end = time.time()
        delta = time_end - time_start
        print('Function %s took %.2f seconds' % (func.__name__,delta))
        return res
    return wrap

def parse_form_date(dt_str):
    """ parse the datetime string as returned from the form """
    return datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M')


def parse_gtfs_date(value):
    year = int(value[0:4])
    month = int(value[4:6])
    day = int(value[6:8])
    return datetime.date(year,month,day)

def parse_bool(value):
    int_value = int(value)
    return True if int_value else False 

def normalize_time(value):
    """ we normalize time (without date) into integer based on minutes
    we ignore the seconds """
    h,m,s = [int(x) for x in value.split(':')]  # @UnusedVariable
    return h * 60*60 + m * 60 + s
    
def denormalize_time_to_string(value):
    s = value % 60
    value = value - s
    value = value / 60
    m = value % 60
    h = value / 60
    return '%02d:%02d:%02d' % (h,m,s)
    
def get_weekdayname(dt):
    return dt.strftime('%A')
    
def format_date(dt):
    return dt.strftime('%A, %b %d, %Y, %H:%M')

def get_utc_time_from_timestamp(ts):
    return datetime.datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)
    
def delete_from_model(model):
    from django.db import connection
    cursor = connection.cursor()
    table_name = model._meta.db_table
    if 'sqlite3' not in settings.DATABASES['default']['ENGINE']:
        cascade = ' CASCADE'
    else:
        cascade = ''
    sql = "DELETE FROM %s%s;" % (table_name,cascade )
    cursor.execute(sql)    
    print 'DELETED %s' % (table_name)


