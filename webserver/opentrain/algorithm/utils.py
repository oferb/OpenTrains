import os
import gtfs.models
import analysis.models
import numpy as np
from scipy import spatial
import shelve
import matplotlib.pyplot as plt
import simplekml
import config
import itertools
import datetime

def get_XY_pos(relativeNullPoint, p):
    """ Calculates X and Y distances in meters.
    """
    deltaLatitude = p.latitude - relativeNullPoint.latitude
    deltaLongitude = p.longitude - relativeNullPoint.longitude
    latitudeCircumference = 40075160 * cos(relativeNullPoint.latitude * pi / 180)
    resultX = deltaLongitude * latitudeCircumference / 360
    resultY = deltaLatitude * 40008000 / 360
    return resultX, resultY




def query_coords(point_tree, query_coords, query_accuracies):
    if isinstance( query_accuracies, ( int, long, float ) ):
        res = point_tree.query_ball_point(query_coords, query_accuracies)
    else:
        res = [point_tree.query_ball_point(query_coords[i], query_accuracies[i]) for i in xrange(len(query_accuracies))]
    return res

def datetime_to_db_time(adatetime):
    return adatetime.hour * 3600 + 60 * adatetime.minute + adatetime.second

def datetime_range_to_db_time(datetime1, datetime2):
    d1 = datetime_to_db_time(datetime1)
    d2 = datetime_to_db_time(datetime2)
    if d1 > d2: # in gtfs, instead of midnight passing to the next day, you count in more time for the same day, i.e 25:00 instead of 01:00
        d2 = d2 + 24*3600    
    return d1,d2

def db_time_to_datetime(db_time):
    return datetime.time(db_time / 3600 % 24, (db_time % 3600) / 60, db_time % 60)

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def is_strictly_increasing(L):
    return all(x<y for x, y in zip(L, L[1:])) 

def is_increasing(L):
    return all(x<=y for x, y in zip(L, L[1:])) 