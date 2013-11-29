import os

from ftplib import FTP
from django.conf import settings

from ot_utils import ot_utils


MOT_FTP = "199.203.58.18"
FILE_NAME = "irw_gtfs.zip"

def download_gtfs_file():
    local_dir = os.path.join('/tmp','gtfs','data',ot_utils.get_utc_time_underscored())
    ot_utils.mkdir_p(local_dir)
    local_path = os.path.join(local_dir,FILE_NAME)
    ot_utils.ftp_get_file(MOT_FTP,FILE_NAME,local_path)
    
    
        
    
    


