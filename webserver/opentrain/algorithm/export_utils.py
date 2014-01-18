import gtfs.models
import analysis.models
import numpy as np
from scipy import spatial
import shelve
import matplotlib.pyplot as plt
import simplekml
import config
import itertools
import os


def save_to_kml(coords_to_save, filename, coords_names=None, do_print=False):
    count = 0
    kml = simplekml.Kml()
    if coords_names is None:
        coords_names = [str(x) for x in xrange(len(coords_to_save))]
    for coord in coords_to_save:
        #if do_print:
        #    print('%d, %s, %s' % (count, coord[0], coord[1]))
        kml.newpoint(name=coords_names[count], coords=[(coord[1],coord[0])])
        count = count + 1
    kml.save(filename)

# TODO: check off-by-1 index of shape files. eg shape file 'shape_64__55_00002.kml' seems to be shape_id = 63
def save_all_shapes_to_kml(shape_int_ids, shape_coords, unique_shape_ids):
    for shape_num in xrange(len(set(shape_int_ids))):
        filename = os.path.join(config.gtfs_processed_data, "shape_%d__%s.kml" % (shape_num, unique_shape_ids[shape_num]))
        coords_to_save = shape_coords[shape_int_ids == shape_num,:]
        save_to_kml(coords_to_save, filename)
