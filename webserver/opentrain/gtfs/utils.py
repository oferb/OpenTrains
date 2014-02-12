import os
import glob

from django.conf import settings
from common import ot_utils

MOT_FTP = "199.203.58.18"
FILE_NAME = "irw_gtfs.zip"
GTFS_DATA_DIR = os.path.join(settings.DATA_DIR,'gtfs','data')
GTFS_ZIP_DIR = os.path.join(settings.DATA_DIR,'gtfs','zip_data')

def download_gtfs_file(download_only=False):
    """ download gtfs zip file from mot, and put it in DATA_DIR in its own subfolder """
    if not download_only:
        local_dir = os.path.join(GTFS_DATA_DIR,ot_utils.get_utc_time_underscored())
    else:
        local_dir = os.path.join(GTFS_ZIP_DIR,ot_utils.get_utc_time_underscored())     
    ot_utils.mkdir_p(local_dir)
    local_path = os.path.join(local_dir,FILE_NAME)
    ot_utils.ftp_get_file(MOT_FTP,FILE_NAME,local_path)
    if not download_only:
        ot_utils.unzip_file(local_path,local_dir)   
    
        
def find_gtfs_data_dir():
    """ returns the lastest subfolder in DATA_DIR """
    dirnames = glob.glob("%s/*" % (GTFS_DATA_DIR))
    if not dirnames:
        raise Exception("No data dir found in %s" % (GTFS_DATA_DIR))
    # return the latest
    return sorted(dirnames)[-1]


    
