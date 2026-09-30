from collections import OrderedDict
import hashlib
import numpy as np
class PreviewCache:
    def __init__(self,max_items=8): self.max_items=max(1,int(max_items)); self._items=OrderedDict()
    def key(self,image,params):
        h=hashlib.sha1(np.ascontiguousarray(image).view(np.uint8)).hexdigest()
        return (h,repr(params))
    def get(self,key):
        v=self._items.get(key)
        if v is not None:self._items.move_to_end(key)
        return v
    def put(self,key,value):
        self._items[key]=value;self._items.move_to_end(key)
        while len(self._items)>self.max_items:self._items.popitem(last=False)
    def clear(self):self._items.clear()