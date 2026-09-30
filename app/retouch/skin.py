import cv2
import numpy as np

def frequency_separation(image,radius=8):
    low=cv2.GaussianBlur(np.clip(image,0,1).astype(np.float32),(0,0),max(0.5,float(radius)))
    high=np.clip(image-low+0.5,0,1)
    return low.astype(np.float32),high.astype(np.float32)

def make_skin_mask(image,hue_min=0,hue_max=25,sat_max=0.75,value_min=0.2):
    hsv=cv2.cvtColor(np.clip(image*255,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32)
    h=hsv[:,:,0]; s=hsv[:,:,1]/255.; v=hsv[:,:,2]/255.
    if hue_min<=hue_max: hm=(h>=hue_min)&(h<=hue_max)
    else: hm=(h>=hue_min)|(h<=hue_max)
    mask=(hm&(s<=sat_max)&(v>=value_min)).astype(np.float32)
    mask=cv2.GaussianBlur(mask,(0,0),2)
    return np.clip(mask,0,1).astype(np.float32)

def skin_smooth(image,mask=None,radius=4,strength=0.3):
    smooth=cv2.bilateralFilter(np.clip(image*255,0,255).astype(np.uint8),d=0,sigmaColor=24,sigmaSpace=max(1,float(radius))).astype(np.float32)/255
    a=float(strength)
    if mask is None: mask=np.ones(image.shape[:2],np.float32)
    return np.clip(image*(1-mask[...,None]*a)+smooth*(mask[...,None]*a),0,1).astype(np.float32)

def skin_tone_correct(image,target_rgb=(0.72,0.45,0.38),strength=0.25,mask=None):
    out=image.astype(np.float32).copy()
    if mask is None: mask=make_skin_mask(image)
    hsv=cv2.cvtColor(np.clip(out*255,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32)
    target=np.asarray(target_rgb,np.float32); target_hsv=cv2.cvtColor((target.reshape(1,1,3)*255).astype(np.uint8),cv2.COLOR_RGB2HSV)[0,0].astype(np.float32)
    dh=((target_hsv[0]-hsv[:,:,0]+90)%180)-90
    hsv[:,:,0]=(hsv[:,:,0]+dh*float(strength)*mask)%180
    hsv[:,:,1]=np.clip(hsv[:,:,1]*(1+float(strength)*0.12*mask),0,255)
    return cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)/255

def texture_restore(image,high_layer,amount=0.5):
    texture=np.clip((high_layer-0.5)*2,-1,1)
    return np.clip(image+texture*float(amount),0,1).astype(np.float32)