import gtfs.models
from scipy import spatial
import shelve
from Shape import Shape
import os
import config
import numpy as np
import copy

from utils import *

class ShapeList(list):
    def __init__(self, django_shape_coords_and_ids) :
        self.point_shape_ids = [x[0] for x in list(django_shape_coords_and_ids.all().values_list('shape_id'))]
        self.point_shape_ids = np.array(self.point_shape_ids)
        lat_list = [float(x[0]) for x in list(django_shape_coords_and_ids.all().values_list('shape_pt_lat'))]
        lon_list = [float(x[0]) for x in list(django_shape_coords_and_ids.all().values_list('shape_pt_lon'))]      
        all_coords = zip(lat_list, lon_list)
        all_coords = np.array(all_coords)
        self.point_tree = spatial.cKDTree(all_coords)
        unique_shape_ids = list(set(self.point_shape_ids))
        unique_shape_ids.sort()
        self.point_shape_int_ids = [unique_shape_ids.index(x) for x in self.point_shape_ids]
        self.point_shape_int_ids = np.array(self.point_shape_int_ids)        
        for shape_id in unique_shape_ids:
            shape_coords = all_coords[self.point_shape_ids == shape_id]
            shape = Shape(shape_id, shape_coords)
            self.append(shape)
            
        self.sampled_point_inds, self.sampled_point_tree = self.get_sampling_of_all_routes()

    def __getstate__(self):
        ret = self.__dict__.copy()
        ret['all_coords'] = self.point_tree.data
        ret['sampled_coords'] = self.sampled_point_tree.data
        del ret['point_tree']
        del ret['sampled_point_tree']
        return ret

    def __setstate__(self, dict):
        self.point_tree = spatial.cKDTree(dict['all_coords'])
        self.sampled_point_tree = spatial.cKDTree(dict['sampled_coords'])
        del dict['all_coords']
        del dict['sampled_coords']
        self.__dict__.update(dict)           
    
    def query_all_points(self, coords, accuracies)   :
        
        res_coord_ids = query_coords(self.point_tree, coords, accuracies)    
        
        res_shape_int_ids = copy.deepcopy(res_coord_ids)
        for i in xrange(len(res_shape_int_ids)):
            res_shape_int_ids[i] = list(set(self.point_shape_int_ids[res_shape_int_ids[i]]))
        
        return res_coord_ids, res_shape_int_ids

    def query_sampled_points(self, coords, accuracies)   :
        pass
    
    def get_sampling_of_all_routes(self):
        shape_point_tree = self.point_tree
        inds_to_go_over = np.zeros(len(shape_point_tree.data)) == 0
        inds_to_keep = np.zeros(len(shape_point_tree.data)) == -1
        dist_threshold = meter_distance_to_coord_distance(config.route_sampling__min_distance_between_points_meters)
        count = 0
        while count < len(inds_to_go_over):
            while(count < len(inds_to_go_over) and not inds_to_go_over[count]):
                count = count + 1
            if count < len(inds_to_go_over):
                inds_to_keep[count] = True
                inds_to_remove = shape_point_tree.query_ball_point(shape_point_tree.data[count], dist_threshold)
                inds_to_go_over[inds_to_remove] = False
            
            
        sampled_all_routes_tree = spatial.cKDTree(shape_point_tree.data[inds_to_keep])
        return inds_to_keep, sampled_all_routes_tree
  

def get_all_shapes():
    datafile = shelve.open(os.path.join(config.gtfs_processed_data, 'shelve.data'))

    if not datafile.has_key('shapesList'):
        gtfs_shapes_data = gtfs.models.Shape.objects.all().values_list('shape_id', 'shape_pt_lat', 'shape_pt_lon')
        datafile['shapesList'] = ShapeList(gtfs_shapes_data)
    all_shapes = datafile['shapesList']
    
    datafile.close() 
    
    return all_shapes

ShapeList.all_shapes = get_all_shapes()