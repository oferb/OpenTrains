import os
#import PIL

#from PIL import Image
import numpy as np

import matplotlib.image as mpimg
import time
import matplotlib.pyplot as plt
import gc
import datetime as dt
import shelve
import config
import shutil
import utils
from enums import Directions
from utils import imshow
import code_written_to_run_once

# useful linux commands for processing images:
# streamer -t 1000000 -s 1280x720 -r 10 -c /dev/video1 -o /home/oferb/docs/train_project/data/webcam3/frames_fullres/image0000000.jpeg
# ls|xargs -I X convert X -resize 300 ~/docs/train_project/data/webcam3/frames_res300/X
# convert mask.png -resize 300 mask_res300.png
#  ls -1 ~/docs/train_project/data/webcam2/frames_resized/ |  wc -l
# ls|xargs -I X convert X -crop 150x100+150+0 ~/docs/train_project/data/webcam2/frames_res300_crop_150x100+150+0/X
# convert mask_res300.png -crop 150x100+150+0 mask_res300_crop_150x100+150+0.png

def main():
    config.set_config(base_dir = '/home/oferb/docs/train_project', experiment_id='webcam2_first2000', lowres=300, crop='150x100+150+0')
    
    # first time image processing:
    #code_written_to_run_once.rename_image_files()
    #utils.copy_image_subset(os.path.join(config.all_data, 'webcam2', 'frames_res300_crop_150x100+150+0'), os.path.join(config.all_data, 'webcam2_first2000', 'frames_res300_crop_150x100+150+0'), range(0,2000))

    datafile = process_video(motion_thresh=2)    
    datafile = shelve.open(os.path.join(config.experiment_output, 'shelve.data'))
    train_spotted = use_hmm(datafile['img_times'], datafile['change_vals'])
    datafile['train_spotted'] = train_spotted
    datafile.close()
    
    # detection step:
    #datafile = shelve.open(os.path.join(config.experiment_output, 'shelve.data'))
    #train_spotted_filtered2 = filter_out_short_motions(datafile['train_spotted'], min_secs_for_train_to_pass=15, fps=10)
    #save_positive_negative_examples(datafile['img_times'], train_spotted_filtered2)
    #detect()
    
    # create 'promotional video':
    #create_video_cv(os.path.join(config.experiment_output, 'frames_hmm_nomask'), max_frame = 3500)


def detect():

    positive_descriptors = get_descriptors(os.path.join(config.experiment_output, 'positive_examples'))
    negative_descriptors = get_descriptors(os.path.join(config.experiment_output, 'negative_examples'))
    from sklearn import svm
    clf = svm.SVC()
    X = np.array(positive_descriptors + negative_descriptors)
    y = np.hstack((np.ones(len(positive_descriptors)), np.zeros(len(negative_descriptors))))
    clf.fit(X, y) 
    
    positive_test = get_descriptors(os.path.join(config.experiment_output, 'positive_test'))
    clf.predict(positive_test)
    

def get_descriptors(image_dir):

    frames_list = os.listdir(image_dir)
    frames_list.sort()
    mask = load_mask()
    sift = cv2.SIFT()
    descriptors_all = []
    while len(frames_list) > 0:
        img1 = np.flipud(mpimg.imread(os.path.join(image_dir, frames_list.pop())))*mask

        # find the keypoints and descriptors with SIFT
        keypoints_current, descriptors_current = sift.detectAndCompute(img1, None)
        filter_list = []
        for kp in keypoints_current:
            try:
                x = np.round(kp.pt[1]) # note opposite x,y order is on purpose
                y = np.round(kp.pt[0])
                filter_list.append(mask[x, y,0])
            except:
                filter_list.append(False)
        filter_list = np.array(filter_list)
        
        #kp1[np.nonzero(filter_list)[0]]
        
        keypoints_current_in_mask = [keypoints_current[i] for i in np.nonzero(filter_list)[0].tolist()]
        descriptors_current_in_mask = [descriptors_current[i] for i in np.nonzero(filter_list)[0].tolist()]
        descriptors_all += descriptors_current_in_mask
        
        #img1_kp = cv2.drawKeypoints(img1, keypoints_current)
        #img2_kp = cv2.drawKeypoints(img1, keypoints_current_in_mask)
        #imshow(np.hstack((img1_kp, img2_kp)))

    return descriptors_all
        
    
    


def save_positive_negative_examples(img_times, train_spotted, n=20):
    train_inds, = np.nonzero(train_spotted)
    non_train_inds, = np.nonzero(1-train_spotted)
    
    positive_inds = train_inds[::len(train_inds)/(2*n)]
    negative_inds = non_train_inds[::len(non_train_inds)/(2*n)]
    
    utils.copy_image_subset(config.experiment_data_frames, os.path.join(config.experiment_output, 'positive_examples'), positive_inds[2::+1])
    utils.copy_image_subset(config.experiment_data_frames, os.path.join(config.experiment_output, 'positive_examples'), positive_inds[2::])
    utils.copy_image_subset(config.experiment_data_frames, os.path.join(config.experiment_output, 'negative_examples'), negative_inds)
    

def process_video(background_alpha=0.1, motion_thresh=0.5, skip_frames=0, fps_period_length=100):
    
    utils.ensure_dir(config.experiment_data_frames)
    utils.ensure_dir(config.experiment_output_frames, True)

    
    mask = load_mask()

    frames_list = os.listdir(config.experiment_data_frames)
    frames_list.sort()
    frames_list_to_store = frames_list
    frames_list.reverse()
    for i in xrange(skip_frames):
        frames_list.pop()
    
    background = np.flipud(mpimg.imread(os.path.join(config.experiment_data_frames, frames_list.pop()))).astype('int16')*mask
    #background = np.mean(background,2)
    #mask = np.mean(mask,2)
    
    img_times = []
    train_spotted = []
    #prev = background
    #prevs = []
    fps_period_start = time.clock()
    change_vals = []
    count = 0
    change_val = 0
    while ( len(frames_list) > 0 ):# and count < 15400:
        if count % fps_period_length == 0:
            elapsed = (time.clock() - fps_period_start)
            if elapsed > 0:
                print('%d\t%.2f\t%.1f fps' % (count, change_val, fps_period_length/elapsed))
            else:
                print('Elapsed time should be positive but is %d' % (elapsed))
            fps_period_start = time.clock()
        
        img_filename = frames_list.pop()
        img = np.flipud(mpimg.imread(os.path.join(config.experiment_data_frames, img_filename)))
        img = img * mask
        
        img_times.append(get_datetime_from_filename(img_filename))

        
        #prevs.append(img)
        #if len(prevs) > 10:
            #prevs.pop()        

        #imshow(np.hstack((np.hstack((background, img)), img_without_background)))
        img_without_background = abs(img.astype('float32') - background.astype('float32')) * mask
        #diff = abs(img.astype('float32') - prev.astype('float32')) * mask
        change_val = np.mean(img_without_background)#np.percentile(img_without_background.flatten(), 90)
        change_vals.append(change_val)
        if change_val > motion_thresh:  
            stacked_image = np.hstack((np.hstack((img, background)), img_without_background))
            utils.imsave(os.path.join(config.experiment_output_frames, img_filename), stacked_image)
            train_spotted.append(True)
        else:
            train_spotted.append(False)
        
	# alternative update options in the following comments:    
        #if len(prevs) == 10: # update background
        #beta = 1
            #background_alpha_img = 1/(beta*(np.abs(background - img)**2) + 1/background_alpha) new
            #background_alpha_img = 1/((beta*((background - img)**2) + 1)/background_alpha) old
            #background_alpha_img = 1/((beta*((prevs[-1] - img)**2) + 1)/background_alpha)
            #background = background*(1-background_alpha_img) + img*(background_alpha_img)                
        background = background*(1-background_alpha) + img*(background_alpha)                
            
        #prev = img

        count += 1
        
        if len(frames_list) == 0:
            print('No more frames to process, unless we check and add some more')
        
    datafile = shelve.open(os.path.join(config.experiment_output, 'shelve.data'))
    datafile['img_times'] = img_times
    datafile['train_spotted'] = train_spotted
    datafile['change_vals'] = change_vals
    datafile['frame_filenames'] = frames_list_to_store
    datafile.close()

    return datafile


def use_hmm(img_times, change_vals, fps=10, min_secs_for_train_to_pass=8):
    
    from sklearn.hmm import GaussianHMM    
    X = np.column_stack(change_vals)    
    n_components = 2
    model = GaussianHMM(n_components, covariance_type="diag", n_iter=1000)
    model.fit([X.T])
    
    #thresh = 10**-15
    #model.transmat_ = np.array([[1-thresh,thresh],[1-thresh,thresh]])
    hidden_states = model.predict(X.T)
    
    # print trained parameters and plot
    print("Transition matrix")
    print(model.transmat_)
    print()
    
    print("means and vars of each hidden state")
    for i in range(n_components):
        print("%dth hidden state" % i)
        print("mean = ", model.means_[i])
        print("var = ", np.diag(model.covars_[i]))
        print()    
    
    if model.means_[0][0] > model.means_[1][0]: # assume most most frames have no train, switch labels if necessary
        hidden_states = 1 - hidden_states
        
    train_spotted = filter_out_short_motions(hidden_states, min_secs_for_train_to_pass, fps)
    
    plot_timeline(img_times, change_vals, hidden_states, train_spotted)
    
    utils.copy_image_subset(config.experiment_data_frames, config.experiment_output_frames_hmm, np.nonzero(train_spotted)[0])
    
    return train_spotted

                
def plot_timeline(img_times, change_vals, hidden_states, train_spotted):
    fig = plt.figure()
    plt.plot_date(img_times, change_vals, 'b-')
    plt.plot_date(img_times, 2*hidden_states, 'g-')
    plt.plot_date(img_times, train_spotted, 'r-')    
    import gt_data
    gt = gt_data.get_gt(config.experiment)
    if gt is not None:
        gt_times = [x[0] for x in gt]
        height = 0.05
        
        import collections
        repetitions = collections.Counter(gt_times).items()
        for i in xrange(1,500):
            repetitions_to_show = [r[0] for r in repetitions if r[1] >= i]
            if len(repetitions_to_show) == 0:
                break
            plt.plot_date(repetitions_to_show, -height + 2*i*height*np.ones([len(repetitions_to_show), 1]), 'k.', markersize=10)
        
    fig.autofmt_xdate()
    
    plt.ylim([0,2])

    plt.show()


def filter_out_short_motions(hidden_states, min_secs_for_train_to_pass, fps):
    from itertools import groupby
    grouped_L = [(k, sum(1 for i in g)) for k,g in groupby(hidden_states)]

    hidden_states2 = []
    for g in grouped_L:
        
        if g[0] == 1:
            if min_secs_for_train_to_pass*fps > g[1]:
                val = 0
            else:
                val = 1
        else:
            val = 0
            
        for i in xrange(g[1]):
            hidden_states2.append(val)
    hidden_states2 = np.array(hidden_states2)
    return hidden_states2
    

def get_datetime_from_filename(img_filename):
    time_struct = time.strptime(img_filename.split('__')[0], '%Y-%m-%d--%H-%M-%S')
    result = dt.datetime.fromtimestamp(time.mktime(time_struct))
    return result


def load_mask():
    mask = mpimg.imread(config.mask).astype('bool')    
    
    if len(mask.shape) == 2: # when the mask is greyscale we make it rgb:
        temp = np.zeros((mask.shape[0],mask.shape[1],3))
        temp[:,:,0] = mask
        temp[:,:,1] = mask
        temp[:,:,2] = mask
        mask = temp
        mask = mask.astype('bool')
    return mask


    
main()
