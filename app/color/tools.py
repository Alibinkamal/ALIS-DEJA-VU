import re
from pathlib import Path
import cv2
import numpy as np

def _curve(values, points):
    pts=sorted((float(x),float(y)) for x,y in points)
    if not pts: return values
    if pts[0][0]>0: pts=[(0.0,pts[0][1])]+pts
    if pts[-1][0]<1: pts=pts+[(1.0,pts[-1][1])]
    lut=np.interp(np.linspace(0,1,256),[p[0] for p in pts],[p[1] for p in pts]).astype(np.float32)
    idx=np.clip(np.rint(values*255),0,255).astype(np.uint8)
    return lut[idx]

def apply_curves(image, master=None, red=None, green=None, blue=None):
    out=np.clip(image,0,1).astype(np.float32)
    if master: out=np.stack([_curve(out[:,:,c],master) for c in range(3)],axis=2)
    for c,pts in enumerate((red,green,blue)):
        if pts: out[:,:,c]=_curve(out[:,:,c],pts)
    return np.clip(out,0,1).astype(np.float32)

def apply_hsl(image,hue=0.0,saturation=0.0,luminance=0.0,channel_adjustments=None):
    rgb=np.clip(image*255,0,255).astype(np.uint8)
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[:,:,0]=(hsv[:,:,0]+float(hue)*90)%180
    hsv[:,:,1]=np.clip(hsv[:,:,1]*(1+float(saturation)),0,255)
    hsv_rgb=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)/255
    if luminance:
        hsv_rgb=np.clip(hsv_rgb*(1+float(luminance)),0,1)
    if channel_adjustments:
        hsv0=cv2.cvtColor((hsv_rgb*255).astype(np.uint8),cv2.COLOR_RGB2HSV).astype(np.float32)
        h=hsv0[:,:,0]
        for name,(dh,ds,dl) in channel_adjustments.items():
            centers={"red":0,"orange":15,"yellow":30,"green":60,"cyan":90,"blue":120,"purple":150,"magenta":165}
            center=centers.get(name.lower(),0)
            dist=np.minimum(np.abs(h-center),180-np.abs(h-center))
            w=np.clip(1-dist/18,0,1)
            hsv0[:,:,0]=(hsv0[:,:,0]+w*float(dh)*90)%180
            hsv0[:,:,1]=np.clip(hsv0[:,:,1]*(1+w*float(ds)),0,255)
            vscale=1+w*float(dl)
            hsv0[:,:,2]=np.clip(hsv0[:,:,2]*vscale,0,255)
        hsv_rgb=cv2.cvtColor(hsv0.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)/255
    return np.clip(hsv_rgb,0,1).astype(np.float32)

def apply_vibrance(image, amount):
    rgb=np.clip(image*255,0,255).astype(np.uint8)
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV).astype(np.float32)
    sat=hsv[:,:,1]/255.0
    weight=1.0-sat
    hsv[:,:,1]=np.clip(hsv[:,:,1]*(1+float(amount)*weight),0,255)
    return cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2RGB).astype(np.float32)/255

def color_balance(image, shadows=(0,0,0),midtones=(0,0,0),highlights=(0,0,0),strength=1.0):
    out=image.astype(np.float32).copy()
    lum=0.299*out[:,:,0]+0.587*out[:,:,1]+0.114*out[:,:,2]
    sh=np.clip((0.55-lum)/0.55,0,1)**1.5
    hi=np.clip((lum-0.45)/0.55,0,1)**1.5
    mid=np.clip(1-sh-hi,0,1)
    for mask,shift in ((sh,shadows),(mid,midtones),(hi,highlights)):
        out += mask[...,None]*np.asarray(shift,np.float32)[None,None,:]*float(strength)
    return np.clip(out,0,1)

def selective_color(image, adjustments):
    out=image.astype(np.float32).copy()
    rgb=np.clip(out*255,0,255).astype(np.uint8)
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV).astype(np.float32)
    centers={"reds":0,"yellows":30,"greens":60,"cyans":90,"blues":120,"magentas":150,"neutrals":0}
    for name,vals in adjustments.items():
        c=centers.get(name.lower())
        if c is None: continue
        h=hsv[:,:,0]
        if name.lower()=="neutrals":
            w=1-np.clip(hsv[:,:,1]/96,0,1)
        else:
            d=np.minimum(np.abs(h-c),180-np.abs(h-c)); w=np.clip(1-d/24,0,1)
        v=np.asarray(vals,np.float32)
        out[:,:,0]=np.clip(out[:,:,0]+w*v[0]/100,0,1)
        out[:,:,1]=np.clip(out[:,:,1]+w*v[1]/100,0,1)
        out[:,:,2]=np.clip(out[:,:,2]+w*v[2]/100,0,1)
    return np.clip(out,0,1)

def split_tone(image,shadow_rgb=(0.08,0.1,0.14),highlight_rgb=(0.95,0.82,0.65),balance=0.0,amount=0.0):
    out=image.astype(np.float32).copy()
    lum=0.299*out[:,:,0]+0.587*out[:,:,1]+0.114*out[:,:,2]
    shadow_w=np.clip((0.5-lum)*2,0,1)
    highlight_w=np.clip((lum-0.5)*2,0,1)
    balance=float(balance)
    shadow_w*=np.clip(1-balance,0,2); highlight_w*=np.clip(1+balance,0,2)
    out=out*(1-amount*(shadow_w+highlight_w))[...,None]
    out+=shadow_w[...,None]*np.asarray(shadow_rgb,np.float32)*amount
    out+=highlight_w[...,None]*np.asarray(highlight_rgb,np.float32)*amount
    return np.clip(out,0,1)

def apply_cube_lut(image,path):
    lines=Path(path).read_text(encoding="utf-8").splitlines()
    size=None; table=[]
    for line in lines:
        s=line.strip()
        if not s or s.startswith("#"): continue
        if s.upper().startswith("LUT_3D_SIZE"):
            size=int(s.split()[-1]); continue
        if s.upper().startswith(("TITLE","DOMAIN_MIN","DOMAIN_MAX")): continue
        parts=s.split()
        if len(parts)==3:
            try: table.append([float(x) for x in parts])
            except ValueError: pass
    if not size or len(table)!=size**3: raise ValueError("Unsupported or malformed .cube LUT")
    lut=np.asarray(table,np.float32).reshape((size,size,size,3))
    coords=np.clip(image,0,1)*(size-1)
    x0=np.floor(coords).astype(np.int32); x1=np.minimum(x0+1,size-1); f=coords-x0
    out=np.zeros_like(image,np.float32)
    for dx in (0,1):
        for dy in (0,1):
            for dz in (0,1):
                wx=(1-f[:,:,0]) if dx==0 else f[:,:,0]
                wy=(1-f[:,:,1]) if dy==0 else f[:,:,1]
                wz=(1-f[:,:,2]) if dz==0 else f[:,:,2]
                out+=lut[x0[:,:,0] if dx==0 else x1[:,:,0],
                         x0[:,:,1] if dy==0 else x1[:,:,1],
                         x0[:,:,2] if dz==0 else x1[:,:,2]]*(wx*wy*wz)[...,None]
    return np.clip(out,0,1).astype(np.float32)