import unittest,numpy as np
from app.processing.retouch import frequency_separation,dodge_burn,heal_spot,clone_stamp
class TestRetouch(unittest.TestCase):
 def setUp(self): self.img=np.random.default_rng(4).random((40,40,3),dtype=np.float32)
 def test_frequency(self):
  low,high=frequency_separation(self.img,4);self.assertEqual(low.shape,self.img.shape);self.assertEqual(high.shape,self.img.shape)
 def test_dodge_burn_bounds(self):
  for mode in ("dodge","burn"):
   out=dodge_burn(self.img,(20,20),8,.2,mode);self.assertTrue(np.all((out>=0)&(out<=1)))
 def test_heal_clone(self):
  self.assertEqual(heal_spot(self.img,(20,20),4).shape,self.img.shape);self.assertEqual(clone_stamp(self.img,(5,5),(20,20),4).shape,self.img.shape)
if __name__=="__main__":unittest.main()
