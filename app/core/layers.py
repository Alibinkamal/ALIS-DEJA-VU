from dataclasses import dataclass,field
from enum import Enum
from typing import List,Optional
import numpy as np
from .masks import Mask

class BlendMode(str,Enum):
    NORMAL="Normal"; MULTIPLY="Multiply"; SCREEN="Screen"; OVERLAY="Overlay"; SOFT_LIGHT="Soft Light"; ADD="Add"

def blend(base,over,mode):
    if mode==BlendMode.MULTIPLY: return base*over
    if mode==BlendMode.SCREEN: return 1-(1-base)*(1-over)
    if mode==BlendMode.OVERLAY: return np.where(base<.5,2*base*over,1-2*(1-base)*(1-over))
    if mode==BlendMode.SOFT_LIGHT: return (1-2*over)*base*base+2*over*base
    if mode==BlendMode.ADD: return np.clip(base+over,0,1)
    return over

@dataclass
class Layer:
    name:str
    pixels:np.ndarray
    opacity:float=1.0
    visible:bool=True
    blend_mode:BlendMode=BlendMode.NORMAL
    mask:Optional[Mask]=None
    locked:bool=False
    def copy(self): return Layer(self.name,self.pixels.copy(),self.opacity,self.visible,self.blend_mode,self.mask.copy() if self.mask else None,self.locked)

class LayerStack:
    def __init__(self,base:np.ndarray): self.layers=[Layer("Background",base.copy())]; self.active_index=0
    @property
    def active(self): return self.layers[self.active_index]
    def add(self,name="Retouch Layer",pixels=None,above=True):
        p=np.zeros_like(self.layers[0].pixels) if pixels is None else pixels.copy(); idx=self.active_index+(1 if above else 0); self.layers.insert(idx,Layer(name,p)); self.active_index=idx; return self.active
    def delete_active(self):
        if len(self.layers)>1: self.layers.pop(self.active_index); self.active_index=min(self.active_index,len(self.layers)-1)
    def duplicate_active(self): return self.add(self.active.name+" Copy",self.active.pixels)
    def move_active(self,delta):
        j=self.active_index+delta
        if 0<=j<len(self.layers): self.layers[self.active_index],self.layers[j]=self.layers[j],self.layers[self.active_index]; self.active_index=j
    def composite(self):
        out=self.layers[0].pixels.copy()
        for layer in self.layers[1:]:
            if not layer.visible: continue
            p=layer.pixels
            a=np.full(p.shape[:2],layer.opacity,np.float32)
            if layer.mask is not None: a*=layer.mask.data
            a=a[...,None]
            out=out*(1-a)+blend(out,p,layer.blend_mode)*a
        return np.clip(out,0,1)
