#! /usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'

def main():
    import gtfs.utils
    gtfs.utils.download_gtfs_file(download_only=True)

if __name__ == '__main__':
    main()










