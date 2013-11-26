import config 
import os

def set_config(base_dir, experiment_id, lowres, crop=None):
    config.base = base_dir
    config.experiment = experiment_id
    config.lowres = lowres
    
    # data folders
    config.all_data = os.path.join(config.base, 'shared', 'video_recordings')
    config.experiment_data = os.path.join(config.all_data, experiment_id)
    config.experiment_data_frames_fullres = os.path.join(config.experiment_data, 'frames_fullres')
    config.mask_fullres = os.path.join(config.experiment_data, 'mask_fullres.png')
    
    # output folders
    config.all_output = os.path.join(config.base, 'video_results')
    config.experiment_output = os.path.join(config.all_output, experiment_id)
    config.experiment_output_frames_fullres = os.path.join(config.experiment_output, 'frames_fullres')
    config.experiment_output_frames_hmm_fullres = os.path.join(config.experiment_output, 'frames_hmm_fullres')

    if lowres is None:
        config.experiment_data_frames = config.experiment_data_frames_fullres
        config.mask = config.mask_fullres
        config.experiment_output_frames = config.experiment_output_frames_fullres
    else:
        if crop is None:
            postfix = 'res%d' % (lowres)
        else:
            postfix = 'res%d_crop_%s' % (lowres, crop)
            
        config.experiment_data_frames_lowres = os.path.join(config.experiment_data, 'frames_%s' % (postfix))
        config.experiment_data_frames = config.experiment_data_frames_lowres
        
        config.mask_lowres = os.path.join(config.experiment_data, 'mask_%s.png' % (postfix))
        config.mask = config.mask_lowres
        
        config.experiment_output_frames_lowres = os.path.join(config.experiment_output, 'frames_%s' % (postfix))
        config.experiment_output_frames = config.experiment_output_frames_lowres
        
        config.experiment_output_frames_hmm_lowres = os.path.join(config.experiment_output, 'frames_hmm_%s' % (postfix))
        config.experiment_output_frames_hmm = config.experiment_output_frames_hmm_lowres

def get_image_filename(frames_dir, count):
       
    return "%s/%s.jpeg" %(frames_dir, "image{0:07d}".format(count))
