"""
Tests for image adjustment algorithms
"""

import unittest
import numpy as np
from app.processing import (
    adjust_exposure,
    adjust_brightness,
    adjust_contrast,
    adjust_saturation,
    adjust_temperature
)


class TestImageAdjustments(unittest.TestCase):
    """Test image adjustment functions"""
    
    def setUp(self):
        """Create test images"""
        # Create a simple test image (0.5 gray)
        self.test_image = np.ones((100, 100, 3), dtype=np.float32) * 0.5
    
    def test_exposure_increase(self):
        """Test exposure increase"""
        result = adjust_exposure(self.test_image, 1.0)
        
        # Exposure 1.0 = 2x brightness
        # 0.5 * 2 = 1.0 (clamped)
        self.assertTrue(np.all(result >= 0.0))
        self.assertTrue(np.all(result <= 1.0))
        self.assertTrue(np.mean(result) > np.mean(self.test_image))
    
    def test_exposure_zero(self):
        """Test zero exposure (no change)"""
        result = adjust_exposure(self.test_image, 0.0)
        np.testing.assert_array_almost_equal(result, self.test_image)
    
    def test_brightness_increase(self):
        """Test brightness increase"""
        result = adjust_brightness(self.test_image, 0.2)
        
        self.assertTrue(np.all(result >= 0.0))
        self.assertTrue(np.all(result <= 1.0))
        self.assertTrue(np.mean(result) > np.mean(self.test_image))
    
    def test_contrast_increase(self):
        """Test contrast increase"""
        result = adjust_contrast(self.test_image, 0.5)
        
        self.assertTrue(np.all(result >= 0.0))
        self.assertTrue(np.all(result <= 1.0))
    
    def test_saturation_on_rgb(self):
        """Test saturation adjustment on RGB image"""
        # Create test image with color
        test_img = np.zeros((100, 100, 3), dtype=np.float32)
        test_img[:, :, 0] = 0.8  # Red
        test_img[:, :, 1] = 0.3  # Green
        test_img[:, :, 2] = 0.2  # Blue
        
        result = adjust_saturation(test_img, 0.5)
        
        self.assertTrue(np.all(result >= 0.0))
        self.assertTrue(np.all(result <= 1.0))
    
    def test_temperature_increase(self):
        """Test temperature increase (warmer)"""
        result = adjust_temperature(self.test_image, 0.5)
        
        self.assertTrue(np.all(result >= 0.0))
        self.assertTrue(np.all(result <= 1.0))
        # Red channel should be brighter
        self.assertTrue(np.mean(result[:, :, 0]) > np.mean(self.test_image[:, :, 0]))
    
    def test_temperature_decrease(self):
        """Test temperature decrease (cooler)"""
        result = adjust_temperature(self.test_image, -0.5)
        
        self.assertTrue(np.all(result >= 0.0))
        self.assertTrue(np.all(result <= 1.0))
        # Blue channel should be brighter
        self.assertTrue(np.mean(result[:, :, 2]) > np.mean(self.test_image[:, :, 2]))


if __name__ == '__main__':
    unittest.main()
