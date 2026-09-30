import unittest
import numpy as np
from app.color import apply_curves,apply_hsl,apply_vibrance,color_balance
from app.retouch import frequency_separation,make_skin_mask,skin_smooth

class TestPhase5(unittest.TestCase):
    def setUp(self):
        y,x=np.mgrid[:32,:32]
        self.image=np.clip(np.stack([.45+.2*x/32,.35+.1*y/32,.30+.05*x/32],axis=2),0,1).astype(np.float32)
    def test_curves_identity(self):
        out=apply_curves(self.image,master=[(0,0),(1,1)])
        np.testing.assert_allclose(out,self.image,atol=1/255)
    def test_color_bounds(self):
        for out in (apply_hsl(self.image,.1,.2),apply_vibrance(self.image,.5),color_balance(self.image)):
            self.assertEqual(out.shape,self.image.shape);self.assertTrue(np.all((out>=0)&(out<=1)))
    def test_frequency_reconstruction(self):
        low,high=frequency_separation(self.image,3)
        reconstructed=np.clip(low+2*(high-.5),0,1)
        self.assertLess(float(np.mean(np.abs(reconstructed-self.image))),0.02)
    def test_skin_mask_and_smooth(self):
        mask=make_skin_mask(self.image)
        out=skin_smooth(self.image,mask,3,.2)
        self.assertEqual(mask.shape,self.image.shape[:2]);self.assertEqual(out.shape,self.image.shape)
        self.assertTrue(np.all((out>=0)&(out<=1)))

if __name__=="__main__":unittest.main()
