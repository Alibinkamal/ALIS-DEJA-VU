import cv2
import numpy as np

def sharpen(image,amount=1.0,radius=1.0,threshold=0.0):
    img=np.clip(image,0,1).astype(np.float32); blur=cv2.GaussianBlur(img,(0,0),max(0.2,float(radius)))
    detail=img-blur
    if threshold>0:
        mag=np.max(np.abs(detail),axis=2,keepdims=True); detail*=np.clip((mag-threshold)/(1e-6+1-threshold),0,1)
    return np.clip(img+detail*float(amount),0,1).astype(np.float32)

def clarity(image,amount=0.25,radius=4):
    img=np.clip(image,0,1).astype(np.float32); blur=cv2.GaussianBlur(img,(0,0),max(1,float(radius)))
    return np.clip(img+(img-blur)*float(amount),0,1).astype(np.float32)

def denoise(image,strength=0.25):
    img=np.clip(image*255,0,255).astype(np.uint8)
    s=3+2*int(max(0,min(1,strength))*3)
    out=cv2.fastNlMeansDenoisingColored(img,None,10+20*strength,10+20*strength,7,s)
    return out.astype(np.float32)/255

def add_grain(image,amount=0.05,size=1.0,roughness=0.5,monochrome=True,seed=7):
    rng=np.random.default_rng(seed)
    h,w=image.shape[:2]; scale=max(1,int(round(size)))
    gh=max(1,h//scale); gw=max(1,w//scale)
    noise=rng.normal(0,float(amount)*(0.5+roughness), (gh,gw)).astype(np.float32)
    noise=cv2.resize(noise,(w,h),interpolation=cv2.INTER_LINEAR)
    if monochrome: n=noise[...,None]
    else: n=rng.normal(0,float(amount),image.shape).astype(np.float32)
    return np.clip(image+n,0,1).astype(np.float32)