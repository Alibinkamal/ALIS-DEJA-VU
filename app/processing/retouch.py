import cv2
import numpy as np

def _xy(shape,x,y): return max(0,min(shape[1]-1,int(x))),max(0,min(shape[0]-1,int(y)))
def clone_stamp(image,source,target,radius,opacity=1.0):
    x0,y0=_xy(image.shape,source[0],source[1]);x1,y1=_xy(image.shape,target[0],target[1]);r=max(1,int(radius))
    xa,xb=max(0,x1-r),min(image.shape[1],x1+r+1);ya,yb=max(0,y1-r),min(image.shape[0],y1+r+1)
    yy,xx=np.ogrid[ya:yb,xa:xb];dx=xx-x1;dy=yy-y1;dist2=dx*dx+dy*dy
    valid=dist2<=r*r;alpha=np.clip(1-dist2/max(r*r,1),0,1).astype(np.float32)*float(opacity)
    out=image.copy();sx=x0+dx;sy=y0+dy
    src_ok=(sx>=0)&(sx<image.shape[1])&(sy>=0)&(sy<image.shape[0])&valid
    if np.any(src_ok):
        region=out[ya:yb,xa:xb].copy()
        sampled=image[np.clip(sy,0,image.shape[0]-1),np.clip(sx,0,image.shape[1]-1)]
        a=alpha[...,None]
        region[src_ok]=region[src_ok]*(1-a[src_ok])+sampled[src_ok]*a[src_ok]
        out[ya:yb,xa:xb]=region
    return np.clip(out,0,1).astype(np.float32)

def heal_spot(image,center,radius,opacity=1.0):
    x,y=_xy(image.shape,*center); r=max(2,int(radius)); mask=np.zeros(image.shape[:2],np.uint8); cv2.circle(mask,(x,y),r,255,-1)
    if image.dtype!=np.float32: src=image.astype(np.float32)
    else: src=image
    bgr=cv2.cvtColor(np.clip(src*255,0,255).astype(np.uint8),cv2.COLOR_RGB2BGR); patch=cv2.inpaint(bgr,mask,int(max(3,r/2)),cv2.INPAINT_TELEA); healed=cv2.cvtColor(patch,cv2.COLOR_BGR2RGB).astype(np.float32)/255
    a=(mask.astype(np.float32)/255*opacity)[...,None]; return np.clip(src*(1-a)+healed*a,0,1)

def dodge_burn(image,center,radius,strength=0.15,mode="dodge",flow=1.0):
    h,w=image.shape[:2]; x,y=_xy(image.shape,*center); yy,xx=np.ogrid[:h,:w]; fall=np.clip(1-np.sqrt((xx-x)**2+(yy-y)**2)/max(radius,1),0,1)**2*strength*flow
    out=image.copy()
    if mode=="dodge": out=out+(1-out)*fall[...,None]
    else: out=out*(1-fall[...,None])
    return np.clip(out,0,1)

def smooth_skin(image,radius=3,strength=.35):
    smooth=cv2.bilateralFilter(np.clip(image*255,0,255).astype(np.uint8),d=0,sigmaColor=30,sigmaSpace=max(1,int(radius*2))).astype(np.float32)/255
    return np.clip(image*(1-strength)+smooth*strength,0,1)

def frequency_separation(image,radius=8):
    low=cv2.GaussianBlur(image,(0,0),radius); high=np.clip(image-low+0.5,0,1); return low,high
