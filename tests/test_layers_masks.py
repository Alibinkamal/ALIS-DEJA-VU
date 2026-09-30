import unittest,numpy as np
from app.core import LayerStack
from app.core.masks import Mask
class TestPhase34(unittest.TestCase):
 def setUp(self):self.img=np.full((32,32,3),.5,np.float32)
 def test_blank_layer_is_transparent(self):
  s=LayerStack(self.img); s.add(); np.testing.assert_allclose(s.composite(),self.img)
 def test_mask_paint_invert(self):
  m=Mask(20,20,0);m.paint(10,10,5,1);self.assertGreater(m.data[10,10],.9);m.invert();self.assertLess(m.data[10,10],.1)
 def test_blend_stack(self):
  s=LayerStack(self.img); l=s.add("paint"); l.pixels[:]=1;l.mask.paint(16,16,8,1); self.assertGreater(float(s.composite()[16,16,0]),.5)
if __name__=="__main__":unittest.main()
