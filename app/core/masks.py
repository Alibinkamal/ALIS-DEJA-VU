import numpy as np
from PIL import Image, ImageFilter

class Mask:
    """Editable grayscale mask, 1=visible, 0=hidden."""
    def __init__(self,width:int,height:int,fill:float=1.0): self.data=np.full((height,width),np.clip(fill,0,1),np.float32)
    @property
    def shape(self): return self.data.shape
    def copy(self):
        m=Mask(self.data.shape[1],self.data.shape[0]); m.data=self.data.copy(); return m
    def invert(self): self.data=1.0-self.data
    def blur(self,radius:float):
        if radius>0: self.data=np.asarray(Image.fromarray((self.data*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius)),np.float32)/255.0
    def paint(self,x,y,radius,opacity=1.0,erase=False,hardness=0.5):
        h,w=self.data.shape; yy,xx=np.ogrid[:h,:w]; d=np.sqrt((xx-x)**2+(yy-y)**2); t=np.clip(1-d/max(radius,1),0,1); t=t**(1.0+max(0,hardness)*4)
        if erase: self.data*=1-t*opacity
        else: self.data += (1-self.data)*t*opacity
        self.data=np.clip(self.data,0,1)
    def resized(self,w,h):
        p=Image.fromarray((self.data*255).astype(np.uint8)).resize((w,h),Image.Resampling.BILINEAR); m=Mask(w,h); m.data=np.asarray(p,np.float32)/255.; return m
