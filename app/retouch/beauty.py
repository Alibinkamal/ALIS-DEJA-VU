import cv2
import numpy as np

def _mask(mask,image):
    if mask is None:return np.ones(image.shape[:2],np.float32)
    return np.clip(mask,0,1).astype(np.float32)

def teeth_whiten(image,mask=None,strength=.35):
    img=np.clip(image,0,1).astype(np.float32);m=_mask(mask,img)
    hsv=cv2.cvtColor((img*255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32)
    low=np.clip((hsv[:,:,2]/255-.45)*2,0,1)*np.clip(1-hsv[:,:,1]/180,0,1)
    a=np.clip(m*low*float(strength),0,1)
    hsv[:,:,1]=np.clip(hsv[:,:,1]*(1-.45*a),0,255);hsv[:,:,2]=np.clip(hsv[:,:,2]+35*a,0,255)
    return cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)/255

def eye_enhance(image,mask=None,strength=.35):
    img=np.clip(image,0,1).astype(np.float32);m=_mask(mask,img)
    sharp=cv2.GaussianBlur(img,(0,0),1.2);detail=img-sharp
    out=np.clip(img+detail*float(strength)*m[...,None],0,1)
    hsv=cv2.cvtColor((out*255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[:,:,2]=np.clip(hsv[:,:,2]+22*float(strength)*m,0,255)
    return cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)/255

def lip_tint(image,mask=None,rgb=(.72,.16,.20),strength=.25):
    img=np.asarray(image,np.float32);m=_mask(mask,img)*float(strength)
    target=np.asarray(rgb,np.float32)[None,None,:]
    return np.clip(img*(1-m[...,None])+target*m[...,None],0,1).astype(np.float32)

def hair_detail(image,mask=None,strength=.3):
    img=np.asarray(image,np.float32);m=_mask(mask,img);blur=cv2.GaussianBlur(img,(0,0),1.5)
    return np.clip(img+(img-blur)*float(strength)*m[...,None],0,1).astype(np.float32)

def contour_light(image,mask=None,strength=.18):
    img=np.asarray(image,np.float32);m=_mask(mask,img);h,w=img.shape[:2];yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    cx,cy=w*.5,h*.48;dx=(xx-cx)/(w*.5);dy=(yy-cy)/(h*.55);light=np.clip(.55-.35*dx-.25*dy,0,1)
    return np.clip(img*(1+m[...,None]*float(strength)*(light[...,None]-.5)),0,1).astype(np.float32)
