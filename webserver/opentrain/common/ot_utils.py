import datetime
import zipfile
import os
import time
from django.conf import settings
from django.utils import timezone
import pytz

def get_utc_time_underscored():
    """ return UTC time as underscored, to timestamp folders """
    t = datetime.datetime.utcnow()
    return t.strftime('%Y_%m_%d_%H_%M_%S')

def get_local_time_underscored():
    """ return time as underscored, to timestamp folders """
    t = datetime.datetime.now()
    return t.strftime('%Y_%m_%d_%H_%M_%S')

def mkdir_p(path):
    """ mkdir -p path """
    if not os.path.exists(path):
        os.makedirs(path)
    
def rmf(path):
    if os.path.exists(path):
        os.removedirs(path)
    
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
    import dateutil.parser
    if not dt_str or dt_str.lower() == 'none':
        return None
    return dateutil.parser.parse(dt_str)


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
    
def get_utc_now():
    return datetime.datetime.utcnow().replace(tzinfo=timezone.utc)
    
def get_localtime_now():
    return get_localtime(get_utc_now())
    
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

def get_localtime(dt):
    tz = pytz.timezone(settings.TIME_ZONE)
    return dt.astimezone(tz)

def get_normal_time(dt):
    local_dt = get_localtime(dt)
    h = local_dt.hour
    m = local_dt.minute
    s = local_dt.second
    return h*3600+60*m+s

def dt_time_to_unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_to_localtime(ts):
    dt = datetime.datetime.utcfromtimestamp(ts).replace(tzinfo=pytz.UTC)
    return get_localtime(dt)

def meter_distance_to_coord_distance(meter_distance):
    """ the following (non-exact) calculation yields a conversion from meter distances 
        to lat-lon distance which should be accurate enough for Israel
        tel_aviv = [32.071589, 34.778227]
        rehovot = [31.896010, 34.811525]
        meter_distance = 19676
        delta_coords = [tel_aviv[0]-rehovot[0], tel_aviv[1]-rehovot[1]]
        delta_coords_norm = (delta_coords[0]**2 + delta_coords[1]**2)**0.5
        meters_over_coords = meter_distance/delta_coords_norm # equals 110101 """
    meters_over_coords = 110101.0
    return meter_distance/meters_over_coords

