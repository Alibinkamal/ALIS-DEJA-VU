from pathlib import Path
import numpy as np
from PIL import Image
try:
 import rawpy; HAS_RAWPY=True
except ImportError: HAS_RAWPY=False
from .formats import STANDARD_FORMATS,RAW_FORMATS
class ImageLoader:
 @staticmethod
 def can_load(path):
  s=Path(path).suffix.lower(); return s in STANDARD_FORMATS or (s in RAW_FORMATS and HAS_RAWPY)
 @staticmethod
 def load(path):
  s=Path(path).suffix.lower()
  if s in STANDARD_FORMATS:
   im=Image.open(path).convert("RGB"); return np.asarray(im,np.float32)/255
  if s in RAW_FORMATS and HAS_RAWPY:
   with rawpy.imread(path) as raw: arr=raw.postprocess()
   return arr.astype(np.float32)/255
  raise IOError(f"Unsupported image format: {s}")
 @staticmethod
 def get_supported_extensions(): return list(STANDARD_FORMATS)+([] if not HAS_RAWPY else list(RAW_FORMATS))
