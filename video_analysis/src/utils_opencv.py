import cv
import cv2
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



def create_video(base_dir, fps=10, max_frame = 10**12):
    import matplotlib.animation as manimation
    import matplotlib
    matplotlib.use("Agg")

    frames_list = os.listdir(base_dir)
    frames_list.sort()
    
    count = 0
    img = np.flipud(mpimg.imread(os.path.join(base_dir, frames_list[0])))

    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Matplotlib',
            comment='Movie support!')
    writer = FFMpegWriter(fps=fps, metadata=metadata)
    
    fig = plt.figure()    

    if not writer:
        print "Error in creating video writer"
        return
    with writer.saving(fig, "writer_test.mp4", 100):
        while len(frames_list) > 0 and count <= max_frame:
            img = cv.LoadImage(os.path.join(base_dir, frames_list.pop()))
            imshow(img)
            writer.grab_frame()
            count += 1
            
    print('Done writing video')

def create_video_cv(base_dir, fps=15, max_frame = 10**12):
    frames_list = os.listdir(base_dir)
    frames_list.sort()
    
    count = 0
    img = cv.LoadImage(os.path.join(base_dir, frames_list[0]))

    frame_size = cv.GetSize(img)
    #writer = cvCreateVideoWriter("out.avi", CV_FOURCC('M', 'J', 'P', 'G'), fps, frame_size, True)
    #writer = cv.CreateVideoWriter(os.path.join(config.experiment_output, 'out.avi'), cv.CV_FOURCC('F', 'L', 'V', '1'), fps, frame_size, True)
    writer = cv.CreateVideoWriter(os.path.join(config.experiment_output, 'out.avi'), cv.CV_FOURCC('F', 'L', 'V', '1'), fps, frame_size, True)
    if not writer:
        print "Error in creating video writer"
        return
    
    while len(frames_list) > 0 and count <= max_frame:
        img = cv.LoadImage(os.path.join(base_dir, frames_list.pop()))
        print cv.WriteFrame(writer, img)
        count += 1
    print('Done writing video')
    
    
    
def process_video_ayalon(base_dir = '/home/oferb/docs/train_project', experiment_id='webcam2', background_alpha=0.05):
    
    ensure_dir('%s/data/%s/frames' % (base_dir, experiment_id))
    ensure_dir('%s/output/%s/backgrounds' % (base_dir, experiment_id))        
    ensure_dir('%s/output/%s/frames' % (base_dir, experiment_id), True)
    ensure_dir('%s/output/%s/frames_input_output' % (base_dir, experiment_id), True)    

    cap = cv2.VideoCapture('%s/data/%s/%s.webm' % (base_dir, experiment_id, experiment_id))
    count = 1
    ret = True
    background = None
    
    #mask = Image.open('%s/data/sade_masks/track_mask1.png' % (base_dir))
    #mask = Image.open('%s/data/webcam1/mask1.png' % (base_dir))
    #img = mask
    mask = np.array(img.getdata(), np.uint8).reshape(img.size[1], img.size[0], 3)
    mask = mask > 128
    while ( cap.isOpened() and ret) :
        ret, img = cap.read()
        
        if ret:
            img = img.astype('double')/255
            if background is None:
                background = img
                background_alpha_img = img
            else:
                beta = 100
                background_alpha_img = 1/((beta*((background - img)**2) + 1)/background_alpha)
                background = background*(1-background_alpha_img) + img*background_alpha_img
            img_PIL = Image.fromarray((img*255).astype('uint8'))
            img_PIL.save('%s/data/%s/frames/frame%d.jpg' % (base_dir, experiment_id, count))
            img_without_background = abs(img - background) * mask
            background_alpha_img_display = (1-background_alpha_img/background_alpha)*mask
            stacked_image_top = np.hstack((img, img_without_background))
            stacked_image_bottom = np.hstack((background, background_alpha_img_display))
            stacked_image = np.vstack((stacked_image_top, stacked_image_bottom))
            img_PIL = Image.fromarray((stacked_image*255).astype('uint8'))
            img_PIL.save('%s/output/%s/frames/frame%d_background_subtracted.jpg' % (base_dir, experiment_id, count))
            img_PIL = Image.fromarray((stacked_image_top*255).astype('uint8'))
            img_PIL.save('%s/output/%s/frames_input_output/frame%d_background_subtracted.jpg' % (base_dir, experiment_id, count))
            
            count += 1
            #cv2.imshow("win",img)
            #cv2.waitKey()
    img_PIL = Image.fromarray(background.astype('uint8'))
    img_PIL.save('%s/output/%s/backgrounds/background_%.1f.jpg' % (base_dir, experiment_id, background_alpha))

#a = cv2.VideoCapture("http://switch3.castup.net/cunet/gm.asp?format=wm&s=032038549F7842188474501BF1D88035&ci=15365&ak=35143679&ClipMediaID=21325&authi=&autht=&dr=")
