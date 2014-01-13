#! /usr/bin/env python

import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'

def main():
    import gtfs.logic
    gtfs.logic.create_all()

if __name__ == '__main__':
    main()









