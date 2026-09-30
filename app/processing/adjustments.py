import cv2, numpy as np

def adjust_exposure(image,v): return np.clip(image*(2.0**float(v)),0,1).astype(np.float32)
def adjust_brightness(image,v): return np.clip(image+float(v),0,1).astype(np.float32)
def adjust_contrast(image,v): return np.clip((image-.5)*(1+float(v))+.5,0,1).astype(np.float32)
def adjust_saturation(image,v):
 hsv=cv2.cvtColor(np.clip(image*255,0,255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32); hsv[:,:,1]=np.clip(hsv[:,:,1]*(1+float(v)),0,255); return cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)/255
def adjust_temperature(image,v):
 out=image.copy(); v=float(v); out[:,:,0]=np.clip(out[:,:,0]*(1+.3*v),0,1); out[:,:,2]=np.clip(out[:,:,2]*(1-.3*v),0,1); return out
def adjust_highlights_shadows(image,highlights,shadows):
 lum=.299*image[:,:,0]+.587*image[:,:,1]+.114*image[:,:,2]; hi=np.clip((lum-.45)/.55,0,1)**.7; sh=np.clip((.55-lum)/.55,0,1)**.7; out=image.copy(); out+=hi[...,None]*(-float(highlights)*.35); out+=sh[...,None]*(float(shadows)*.35); return np.clip(out,0,1)
def apply_curve(image,points):
 pts=sorted((float(x),float(y)) for x,y in points); x=np.linspace(0,1,256); y=np.interp(x,[p[0] for p in pts],[p[1] for p in pts]); idx=np.clip((image*255).astype(np.int16),0,255); return y[idx]
