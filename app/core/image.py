from pathlib import Path
from typing import Dict
import numpy as np
from app.image.loader import ImageLoader

class ImageData:
    def __init__(self,file_path:str):
        self.file_path=Path(file_path)
        self.original_image=ImageLoader.load(str(self.file_path)).astype(np.float32)
        self.working_image=self.original_image.copy()
        self.adjustments:Dict[str,float]={}
    def reset_to_original(self):
        self.working_image=self.original_image.copy(); self.adjustments.clear()
    def update_working_image(self,data): self.working_image=np.clip(data,0,1).astype(np.float32)
    def get_working_image(self): return self.working_image
    def get_dimensions(self):
        h,w=self.original_image.shape[:2]; return w,h
    def set_adjustment(self,name,value): self.adjustments[name]=value
    def get_adjustment(self,name,default=0.0): return self.adjustments.get(name,default)
    def get_filename(self): return self.file_path.name
    def get_filepath(self): return str(self.file_path)
