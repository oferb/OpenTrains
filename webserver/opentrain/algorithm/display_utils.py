import os
os.environ['DJANGO_SETTINGS_MODULE']='opentrain.settings'
import gtfs.models
import analysis.models
import numpy as np
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from scipy import spatial
import shelve
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass
import simplekml
import config
import itertools
import os
import common.ot_utils as ot_utils
import utils


def print_array(arr):
    for r in zip(range(len(arr)),arr):
        print(r) 
        
        
def plot_coords(coords, colors=None, edgecolor=None, axis=None):
    assert colors==None or edgecolor==None, 'Either colors or edgecolor has to be None'
    if coords.size == 2:
        coords = np.concatenate((device_coords_short[0], device_coords_short[0])).reshape((2,2))
        if colors is not None:
            colors = colors + colors
    
    if axis is None:
        axis = plt.gca() 
        #plt.gca().invert_xaxis()
        #plt.gca().invert_yaxis()        
    
    if edgecolor is None and colors is None:
        edgecolor = 'b'

    if colors is not None:
        sc = axis.scatter(coords[:,1], coords[:,0], marker='+', c=colors)
        plt.colorbar(sc)
    else:
        sc = axis.scatter(coords[:,1], coords[:,0], edgecolor=edgecolor, marker='+')
    
    plt.show()
    return sc  

def plot_and_save_shape_matches(shape_point_tree, sampled_all_routes_tree, shape_int_ids, device_coords, shape_probs):
    for shape_id in xrange(len(set(shape_int_ids))):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        plot_coords(sampled_all_routes_tree.data, edgecolor='0.75', axis = ax1)
        shape_points = shape_point_tree.data[shape_int_ids == shape_id]
        plot_coords(shape_points, edgecolor='b', axis = ax1)
        plot_coords(device_coords, edgecolor='r', axis = ax1)
        plt.title('shape_id=%s, score=%d%%' % (shape_id, int(100*shape_probs[shape_id])))
        plt.savefig(os.path.join(config.output_data, 'shape_%d.png' % (shape_id)), bbox_inches=0)
        plt.close('all')
        

if __name__ == "__main__":
    trips = gtfs.models.Trip.objects.filter(trip_id='170214_00517')
    trips[0].print_stoptimes()