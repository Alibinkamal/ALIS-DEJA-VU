import unittest
import numpy as np
from app.performance import PreviewCache
from app.raw import RawOptions

class TestPhase7(unittest.TestCase):
    def test_preview_cache_is_bounded(self):
        cache=PreviewCache(2);image=np.zeros((4,4,3),np.float32)
        for i in range(4):
            key=cache.key(image,{"i":i});cache.put(key,i)
        self.assertLessEqual(len(cache._items),2)
        self.assertEqual(cache.get(cache.key(image,{"i":3})),3)

    def test_raw_options_defaults(self):
        opts=RawOptions()
        self.assertTrue(opts.use_camera_wb)
        self.assertFalse(opts.use_auto_wb)
        self.assertEqual(opts.output_bps,16)

if __name__=="__main__":
    unittest.main()
