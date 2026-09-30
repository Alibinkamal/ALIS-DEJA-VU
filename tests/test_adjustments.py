import unittest
import numpy as np
from app.processing import adjust_exposure,adjust_brightness,adjust_contrast,adjust_saturation,adjust_temperature
class TestAdjustments(unittest.TestCase):
 def setUp(self):self.image=np.full((16,16,3),.5,np.float32)
 def test_exposure(self):self.assertGreater(np.mean(adjust_exposure(self.image,1)),.5)
 def test_brightness(self):self.assertGreater(np.mean(adjust_brightness(self.image,.1)),.5)
 def test_contrast_bounds(self):o=adjust_contrast(self.image,.5);self.assertTrue(np.all((o>=0)&(o<=1)))
 def test_saturation_bounds(self):o=adjust_saturation(self.image,.5);self.assertTrue(np.all((o>=0)&(o<=1)))
 def test_temperature(self):self.assertGreater(np.mean(adjust_temperature(self.image,.5)[:,:,0]),.5)
if __name__=="__main__":unittest.main()
