import cv2
import numpy as np

def color_wheels(image, shadows=(0,0,0), midtones=(0,0,0), highlights=(0,0,0), balance=0.0, strength=1.0):
    out=np.asarray(image,np.float32).copy(); lum=.299*out[:,:,0]+.587*out[:,:,1]+.114*out[:,:,2]
    sh=np.clip((.55-lum)/.55,0,1)**1.4; hi=np.clip((lum-.45)/.55,0,1)**1.4; mid=np.clip(1-sh-hi,0,1)
    b=float(balance); sh*=np.clip(1-b,0,2); hi*=np.clip(1+b,0,2)
    for m,c in ((sh,shadows),(mid,midtones),(hi,highlights)): out+=m[...,None]*np.asarray(c,np.float32)[None,None,:]*float(strength)
    return np.clip(out,0,1).astype(np.float32)

def apply_vignette(image,amount=.25,midpoint=.5,feather=.7):
    h,w=image.shape[:2]; yy,xx=np.ogrid[:h,:w]; d=np.sqrt(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2)/1.4142
    edge=np.clip((d-float(midpoint))/max(.01,1-float(midpoint)),0,1)**max(.1,float(feather)*3)
    return np.clip(image*(1-float(amount)*edge[...,None]),0,1).astype(np.float32)

def bloom(image,amount=.12,radius=8):
    img=np.clip(image,0,1).astype(np.float32); lum=.299*img[:,:,0]+.587*img[:,:,1]+.114*img[:,:,2]
    glow=cv2.GaussianBlur(img*np.clip((lum-.72)/.28,0,1)[...,None],(0,0),max(.5,float(radius)))
    return np.clip(img+glow*float(amount),0,1).astype(np.float32)

def halation(image,amount=.08,radius=5):
    img=np.clip(image,0,1).astype(np.float32); glow=cv2.GaussianBlur(np.clip((img[:,:,0]-.62)/.38,0,1),(0,0),max(.5,float(radius)))
    out=img.copy();out[:,:,0]=np.clip(out[:,:,0]+glow*float(amount),0,1);out[:,:,1]=np.clip(out[:,:,1]+glow*float(amount)*.18,0,1)
    return out.astype(np.float32)

def tone_curve(image,points):
    pts=sorted((float(x),float(y)) for x,y in points)
    if not pts:return image
    if pts[0][0]>0:pts=[(0,pts[0][1])]+pts
    if pts[-1][0]<1:pts.append((1,pts[-1][1]))
    lut=np.interp(np.linspace(0,1,256),[p[0] for p in pts],[p[1] for p in pts]).astype(np.float32)
    return lut[np.clip(np.rint(np.asarray(image)*255),0,255).astype(np.uint8)].astype(np.float32)

def linear_gradient_mask(h,w,angle=90,softness=.2):
    y,x=np.mgrid[0:h,0:w].astype(np.float32);a=np.deg2rad(angle);v=x*np.cos(a)+y*np.sin(a);t=(v-v.min())/max(1e-6,v.max()-v.min());s=max(.001,float(softness))
    return np.clip((t-(.5-s))/(2*s),0,1).astype(np.float32)

def radial_mask(h,w,cx=.5,cy=.5,radius=.5,feather=.25):
    y,x=np.mgrid[0:h,0:w].astype(np.float32);d=np.sqrt((x/w-float(cx))**2+(y/h-float(cy))**2);inner=max(0,float(radius)-float(feather))
    return np.clip((float(radius)-d)/max(.001,float(radius)-inner),0,1).astype(np.float32)

def crop_array(image,x,y,w,h):
    H,W=image.shape[:2];x=max(0,min(W-1,int(x)));y=max(0,min(H-1,int(y)));w=max(1,min(W-x,int(w)));h=max(1,min(H-y,int(h)))
    return np.ascontiguousarray(image[y:y+h,x:x+w]).astype(np.float32)

def transform_array(image,rotation=0,flip_h=False,flip_v=False):
    out=image;r=int(rotation)%360
    if r==90:out=np.rot90(out,1)
    elif r==180:out=np.rot90(out,2)
    elif r==270:out=np.rot90(out,3)
    if flip_h:out=np.fliplr(out)
    if flip_v:out=np.flipud(out)
    return np.ascontiguousarray(out).astype(np.float32)

def proxy(image,max_side=1600):
    h,w=image.shape[:2];scale=min(1,float(max_side)/max(h,w))
    if scale>=1:return image.copy()
    return cv2.resize(image,(max(1,round(w*scale)),max(1,round(h*scale))),interpolation=cv2.INTER_AREA).astype(np.float32)


def perspective_warp(image, top_left=(0,0), top_right=(1,0), bottom_right=(1,1), bottom_left=(0,1)):
    h,w=image.shape[:2]; src=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    dst=np.float32([[float(top_left[0])*w,float(top_left[1])*h],[float(top_right[0])*w,float(top_right[1])*h],[float(bottom_right[0])*w,float(bottom_right[1])*h],[float(bottom_left[0])*w,float(bottom_left[1])*h]])
    M=cv2.getPerspectiveTransform(src,dst); out=cv2.warpPerspective(np.asarray(image,np.float32),M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return np.clip(out,0,1).astype(np.float32)


def lens_correction(image,amount=0.08):
    img=np.asarray(image,np.float32);h,w=img.shape[:2];yy,xx=np.indices((h,w),np.float32);x=(xx-(w-1)/2)/max(1,(w-1)/2);y=(yy-(h-1)/2)/max(1,(h-1)/2);r2=x*x+y*y
    k=float(amount);factor=1+k*r2;mx=(x/factor+1)*.5*(w-1);my=(y/factor+1)*.5*(h-1)
    return cv2.remap(img,mx.astype(np.float32),my.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
