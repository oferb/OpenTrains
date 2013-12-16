import numpy as np
import os
import matplotlib.image as mpimg
import time
import matplotlib.pyplot as plt
import gc
import datetime as dt
import shelve
import config
import shutil
import utils


def copy_image_subset(source_dir, target_dir, subset_inds):
    frames_list = os.listdir(source_dir)
    frames_list.sort()
    utils.ensure_dir(target_dir, True)
    for i in subset_inds:
        if os.path.exists(os.path.join(source_dir, frames_list[i])):
            shutil.copy2(os.path.join(source_dir, frames_list[i]), os.path.join(target_dir, frames_list[i]))
 
def histshow(img):
    hist, bins = np.histogram(img)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.show()    

def draw_flow(img, flow, step=16):
    h, w = img.shape[:2]
    y, x = np.mgrid[step/2:h:step, step/2:w:step].reshape(2,-1)
    fx, fy = flow[y,x].T
    lines = np.vstack([x, y, x+fx, y+fy]).T.reshape(-1, 2, 2)
    lines = np.int32(lines + 0.5)
    vis = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cv2.polylines(vis, lines, 0, (0, 255, 0))
    for (x1, y1), (x2, y2) in lines:
        cv2.circle(vis, (x1, y1), 1, (0, 255, 0), -1)
    return vis

def imshow(img):
    if img.dtype.name == 'bool':
        plt.imshow(img)
    elif np.mean(img) > 1:
        plt.imshow(img.astype('float32')/255)
    else:
        plt.imshow(img)


def imsave(fname, arr, vmin=None, vmax=None, cmap=None, format=None,
           origin=None, dpi=100):
    """
    Saves a 2D :class:`numpy.array` as an image with one pixel per element.
    The output formats available depend on the backend being used.

    Arguments:
      *fname*:
        A string containing a path to a filename, or a Python file-like object.
        If *format* is *None* and *fname* is a string, the output
        format is deduced from the extension of the filename.
      *arr*:
        A 2D array.
    Keyword arguments:
      *vmin*/*vmax*: [ None | scalar ]
        *vmin* and *vmax* set the color scaling for the image by fixing the
        values that map to the colormap color limits. If either *vmin* or *vmax*
        is None, that limit is determined from the *arr* min/max value.
      *cmap*:
        cmap is a colors.Colormap instance, eg cm.jet.
        If None, default to the rc image.cmap value.
      *format*:
        One of the file extensions supported by the active
        backend.  Most backends support png, pdf, ps, eps and svg.
      *origin*
        [ 'upper' | 'lower' ] Indicates where the [0,0] index of
        the array is in the upper left or lower left corner of
        the axes. Defaults to the rc image.origin value.
      *dpi*
        The DPI to store in the metadata of the file.  This does not affect the
        resolution of the output image.
    """
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    arr = arr.astype('uint8')


    figsize = [x / float(dpi) for x in (arr.shape[1], arr.shape[0])]
    fig = Figure(figsize=figsize, dpi=dpi, frameon=False)
    canvas = FigureCanvas(fig)
    im = fig.figimage(arr, cmap=cmap, vmin=vmin, vmax=vmax, origin=origin)
    fig.savefig(fname, dpi=dpi, format=format)


def ensure_dir(directory, erase_contents = False):
    if not os.path.exists(directory):
        os.makedirs(directory)    
    if erase_contents:
        fileList = os.listdir(directory)
        for fileName in fileList:
            os.remove(os.path.abspath(os.path.join(directory, fileName)))   
