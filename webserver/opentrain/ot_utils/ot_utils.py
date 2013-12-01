import datetime
import zipfile
import os

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
    
    
def unzip_file(fname,dir):
    zf = zipfile.ZipFile(fname)
    zf.extractall(path=dir)
    print("Unzipped %s => %s" % (fname,dir))
    
        
    

