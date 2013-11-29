import datetime
import subprocess

def get_utc_time_underscored():
    t = datetime.datetime.utcnow()
    return t.strftime('%Y_%m_%d_%H_%M_%S')

def mkdir_p(path):
    subprocess.call(["mkdir", "-p",path])
    
def ftp_get_file(host,remote_name,local_path):
    from ftplib import FTP
    f = FTP(host)
    f.login()
    fh = open(local_path,'wb')
    f.retrbinary('RETR %s' % (remote_name), fh.write)
    fh.close()
    f.quit()
    subprocess.call(["ls", "-l",local_path])
    print("Copied from host %s: %s => %s" % (host,remote_name,local_path))
    
    
def unzip_file(fname,dir):
    subprocess.call(["unzip","-f","-d",dir,fname])
    subprocess.call(["ls","-l",dir])
    
        
        
    

