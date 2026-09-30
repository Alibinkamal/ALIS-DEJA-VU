from pathlib import Path
import numpy as np
from PIL import Image

def resize_image(data,width=None,height=None):
    if width is None and height is None:return data
    h,w=data.shape[:2]
    if width is None: width=max(1,round(w*height/h))
    if height is None: height=max(1,round(h*width/w))
    im=Image.fromarray(np.clip(data*255,0,255).astype(np.uint8),"RGB").resize((int(width),int(height)),Image.Resampling.LANCZOS)
    return np.asarray(im,np.float32)/255

def export_image(data,path,quality=95,width=None,height=None,metadata=None):
    path=Path(path); out=resize_image(data,width,height); arr=np.clip(out*255,0,255).astype(np.uint8); im=Image.fromarray(arr,"RGB")
    ext=path.suffix.lower()
    if ext in (".jpg",".jpeg"):
        kwargs={"quality":int(quality),"optimize":True}
        if metadata: kwargs["exif"]=metadata
        im.save(path,"JPEG",**kwargs)
    elif ext==".png": im.save(path,"PNG",optimize=True)
    elif ext in (".tif",".tiff"): im.save(path,"TIFF")
    else: raise ValueError(f"Unsupported export format: {ext}")
    return path