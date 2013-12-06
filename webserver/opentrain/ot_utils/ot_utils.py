import datetime
import zipfile
import os
import time

def get_utc_time_underscored():
    t = datetime.datetime.utcnow()
    return t.strftime('%Y_%m_%d_%H_%M_%S')

def mkdir_p(path):
    if not os.path.exists(path):
        os.makedirs(path)
    
def ftp_get_file(host,remote_name,local_path):
    from ftplib import FTP
    f = FTP(host)
    f.login()
    fh = open(local_path,'wb')
    f.retrbinary('RETR %s' % (remote_name), fh.write)
    fh.close()
    f.quit()
    print("Copied from host %s: %s => %s" % (host,remote_name,local_path))
    
    
def unzip_file(fname,dirname):
    zf = zipfile.ZipFile(fname)
    zf.extractall(path=dirname)
    print("Unzipped %s => %s" % (fname,dir))
    
        
def benchit(func):
    def wrap(*args,**kwargs):
        time_start = time.time()
        res = func(*args,**kwargs)
        time_end = time.time()
        delta = time_end - time_start
        print('Function %s took %.2f seconds' % (func.__name__,delta))
        return res
    return wrap

def parse_dt(dt_str):
    return datetime.datetime.strptime(dt_str, '%Y-%m-%d %H:%M')

