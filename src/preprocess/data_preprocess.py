import os
import xarray as xr
import pandas as pd
import sys
import numpy as np
sys.path.insert(0, '../src')

from utils import df_to_xarray,read_xarray
### Image Data Preprocess for CNN ###
def preprocess_images(dir_name):
    
    chl,mld,sss,sst,u10,fg_co2,xco2,icefrac,patm,pco2 = read_xarray(dir_name)
    
    chl_images = preprocess_image_reduced(chl.Chl.data)
    mld_images = preprocess_image_reduced(mld.MLD.data)
    sss_images = preprocess_image_reduced(sss.SSS.data)
    sst_images = preprocess_image_reduced(sst.SST.data)
    xco2_images = preprocess_image_reduced(xco2.XCO2.data,xco2=True)
    
    pco2_images = preprocess_image_reduced(pco2.pCO2.data)
    
    X = np.stack((chl_images, mld_images, sss_images, sst_images, xco2_images), axis = 1)
    X = X.reshape((421,180,360,5))

    return X, pco2_images


def preprocess_image_reduced(data,xco2=False):
    if xco2:
        return xco2_preprocess(data)
    
    return scale_image(convert_nan(data))
  

### FOR SEQUENTIAL + VISION
def create_shifted_frames(data):
    x = data[:, 0 : data.shape[1] - 1, :, :]
    y = data[:, 1 : data.shape[1], :, :]
    return x, y

### FOR VISION ###

def xco2_preprocess(data):
    """
    ## XCO2 Handling
    # - xco2 values are a constant value across the globe, 
    # - creating an image layer with constant value for the model
    # - xco2 layer improves prediction

    """
    output=[]
    min_xco2=np.min(data)
    max_xco2=np.max(data)
    new_min=0
    new_max=255
    
    for i in data:
        num = (i-min_xco2)*(new_max-new_min)/(max_xco2-min_xco2)+new_min
        tmp = (np.repeat(num,180*360)).reshape(180,-1)
        output.append(tmp)
        
    output=np.array(output)

    return output


def convert_nan(arr):
    """
    convert_nan(arr)
    - converts nan values to the lowest value (continents)
    """
    nans=np.isnan(arr)
    min_val=arr[~nans].min()
    arr[nans]=min_val-1
    return arr

def add_dimension(arr):
    """
    add_dimension(arr)
    - add one dimension to axis=3
    """
    images=np.expand_dims(arr, axis=3)
    return images

def scale_image(arr):
    """
    scale_image(arr)
    - scales numerical values from scale 0-255 for like an image
    - have tried, regular normal/ min-max scaler -> does not work well
    """
    ## Normal
    #arr=(arr-np.mean(arr))/np.std(arr)
    
    ## Min-Max
    # min_val=arr.min()
    # max_val=arr.max()
    # arr=arr/(min_val-max_val)

    ## Image Scale
    min_pixel = arr.min() 
    max_pixel = arr.max()
    new_min = 0
    new_max = 255
    arr = (arr-min_pixel)*(255)/(max_pixel-min_pixel)+new_min 
    return arr
  

