import datetime

def get_utc_time_underscored():
    t = datetime.datetime.utcnow()
    return t.strftime('%Y_%m_%d_%H_%M_%S')

def mkdir_p(path):
    from subprocess import call
    call(["mkdir", "-p",path])
    
def ftp_get_file(host,remote_name,local_path):
    from ftplib import FTP
    f = FTP(host)
    f.login()
    write_cb = open(local_path, 'wb').write
    f.retrbinary('RETR %s' % (remote_name), write_cb)
    f.quit()
    print("Copied from host %s: %s => %s" % (host,remote_name,local_path))
    
    
    
    

