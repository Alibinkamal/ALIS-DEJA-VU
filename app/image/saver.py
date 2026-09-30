from pathlib import Path
import numpy as np
from PIL import Image
from .formats import EXPORT_FORMATS
class ImageSaver:
 @staticmethod
 def save(data,path,quality=95,metadata=None):
  ext=Path(path).suffix.lower()
  if ext not in EXPORT_FORMATS: raise IOError(f"Unsupported export format: {ext}")
  a=np.clip(data*255,0,255).astype(np.uint8)
  mode="L" if a.ndim==2 else ("RGBA" if a.shape[-1]==4 else "RGB")
  im=Image.fromarray(a,mode)
  if EXPORT_FORMATS[ext]=="JPEG": im.save(path,"JPEG",quality=int(quality),optimize=True)
  elif EXPORT_FORMATS[ext]=="PNG": im.save(path,"PNG",optimize=True)
  else: im.save(path,"TIFF")
