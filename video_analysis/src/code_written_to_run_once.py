import PIL
import cv
import cv2
from PIL import Image
import numpy as np
import os
import matplotlib.image as mpimg
import time
import matplotlib.pyplot as plt
import gc
from guppy import hpy
import datetime as dt
import shelve
import config
import shutil
import utils

def recalc_final_result(base_dir = '/home/oferb/docs/train_project', experiment_id='webcam2', use_resized=False):
    import shutil
    if use_resized:
        frame_base = 'frames_resized'
    else:
        frame_base = 'frames'
        
    frames_dir = '%s/data/%s/%s' % (base_dir, experiment_id, frame_base)
    resized_files_dir = os.path.join(base_dir, 'output', experiment_id, 'frames_resized_done')
    resized_files_dir_times = os.path.join(base_dir, 'output', experiment_id, 'frames_resized_done_times')
    files = os.listdir(resized_files_dir)
    import re
    ids = []
    for filename in files:
        ids.append(re.findall(r'\d+', filename))
    
    img_times = []
    for an_id, filename in zip(ids, files):
        img_filename = utils.get_image_filename(frames_dir, int(an_id[0]), use_resized)
        img_times.append(dt.datetime.fromtimestamp(os.path.getctime(img_filename)))
        shutil.copy2(os.path.join(resized_files_dir, filename), os.path.join(resized_files_dir_times, '%s_%s' % (img_times[-1], filename)))
    
    values = np.ones([len(img_times), 1])    
    plt.plot_date(img_times, values)

def rename_files_with_time(base_dir = '/home/oferb/docs/train_project', experiment_id='webcam2', use_resized=False):
    if use_resized:
        frame_base = 'frames_resized'
    else:
        frame_base = 'frames'
        
    frames_dir = '%s/data/%s/%s' % (base_dir, experiment_id, frame_base)
    
    files = os.listdir(os.path.join(base_dir, 'output', experiment_id, 'frames_resized_done'))
    import re
    ids = []
    for filename in files:
        ids.append(re.findall(r'\d+', filename))
    
    img_times = []
    for an_id in ids:
        img_filename = config.get_image_filename(frames_dir, int(an_id[0]), use_resized)
        img_times.append(dt.datetime.fromtimestamp(os.path.getctime(img_filename)))
    
def rename_image_files():
    import re
    frames_fullres_filenames = os.listdir(config.experiment_data_frames_fullres)
    frames_fullres_filenames.sort()
    frames_lowres_filenames = os.listdir(config.experiment_data_frames_lowres)
    
    fullres_datetimes = []
    fullres_ids = []
    for filename in frames_fullres_filenames:
        full_fullres_filename = os.path.join(config.experiment_data_frames_fullres, filename)
        fullres_datetimes.append(dt.datetime.fromtimestamp(os.path.getctime(full_fullres_filename)))
        fullres_ids.append(int(re.findall(r'\d+', filename)[0]))

        full_lowres_filename = config.get_image_filename(config.experiment_data_frames_lowres, fullres_ids[-1])
        lowres_filename_renamed = '%s__%s.jpeg' % (fullres_datetimes[-1].strftime('%Y-%m-%d--%H-%M-%S'), fullres_ids[-1])
        full_lowres_filename_renamed  = os.path.join(config.experiment_data_frames_lowres, lowres_filename_renamed)
        os.rename(full_lowres_filename, full_lowres_filename_renamed)
        
        fullres_filename_renamed = lowres_filename_renamed
        full_fullres_filename_renamed = os.path.join(config.experiment_data_frames_fullres, fullres_filename_renamed)
        os.rename(full_fullres_filename, full_fullres_filename_renamed)
        
    print('hi')    
 