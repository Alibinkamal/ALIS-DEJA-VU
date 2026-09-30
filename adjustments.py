"""
Image Adjustments - Professional image processing algorithms

Provides:
- Exposure adjustment
- Brightness/Contrast
- Saturation
- Color temperature
- Curves
- HSL adjustments
"""

import numpy as np
from scipy import interpolate
import cv2


def adjust_exposure(image: np.ndarray, exposure: float) -> np.ndarray:
    """
    Adjust image exposure.
    
    Args:
        image: Image array (0-1 float range)
        exposure: Exposure adjustment (-2 to 2, 0 = no change)
        
    Returns:
        np.ndarray: Adjusted image
    """
    if abs(exposure) < 0.01:
        return image.copy()
    
    # Exposure = 2^value
    multiplier = 2.0 ** exposure
    result = image * multiplier
    return np.clip(result, 0, 1)


def adjust_brightness(image: np.ndarray, brightness: float) -> np.ndarray:
    """
    Adjust image brightness.
    
    Args:
        image: Image array (0-1 float range)
        brightness: Brightness adjustment (-1 to 1)
        
    Returns:
        np.ndarray: Adjusted image
    """
    if abs(brightness) < 0.01:
        return image.copy()
    
    result = image + brightness
    return np.clip(result, 0, 1)


def adjust_contrast(image: np.ndarray, contrast: float) -> np.ndarray:
    """
    Adjust image contrast.
    
    Args:
        image: Image array (0-1 float range)
        contrast: Contrast adjustment (-1 to 1, 0 = no change)
        
    Returns:
        np.ndarray: Adjusted image
    """
    if abs(contrast) < 0.01:
        return image.copy()
    
    # Pivot around middle gray
    result = (image - 0.5) * (1 + contrast) + 0.5
    return np.clip(result, 0, 1)


def adjust_saturation(image: np.ndarray, saturation: float) -> np.ndarray:
    """
    Adjust image saturation.
    
    Args:
        image: Image array (0-1 float range, RGB)
        saturation: Saturation adjustment (-1 to 1, 0 = no change)
        
    Returns:
        np.ndarray: Adjusted image
    """
    if abs(saturation) < 0.01:
        return image.copy()
    
    if len(image.shape) != 3 or image.shape[2] != 3:
        return image.copy()
    
    # Convert RGB to HSV
    hsv = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    
    # Adjust saturation (S channel)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (1 + saturation), 0, 255)
    
    # Convert back to RGB
    rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32) / 255.0
    
    return np.clip(rgb, 0, 1)


def adjust_temperature(image: np.ndarray, temperature: float) -> np.ndarray:
    """
    Adjust color temperature (warm/cool).
    
    Args:
        image: Image array (0-1 float range, RGB)
        temperature: Temperature adjustment (-1 to 1)
                    negative = cooler (more blue)
                    positive = warmer (more red)
        
    Returns:
        np.ndarray: Adjusted image
    """
    if abs(temperature) < 0.01:
        return image.copy()
    
    if len(image.shape) != 3 or image.shape[2] != 3:
        return image.copy()
    
    result = image.copy()
    
    if temperature > 0:
        # Warmer: increase red, decrease blue
        result[:, :, 0] = np.clip(result[:, :, 0] * (1 + temperature * 0.3), 0, 1)
        result[:, :, 2] = np.clip(result[:, :, 2] * (1 - temperature * 0.2), 0, 1)
    else:
        # Cooler: increase blue, decrease red
        result[:, :, 2] = np.clip(result[:, :, 2] * (1 - temperature * 0.3), 0, 1)
        result[:, :, 0] = np.clip(result[:, :, 0] * (1 + temperature * 0.2), 0, 1)
    
    return result


def apply_curve(image: np.ndarray, curve_points: list) -> np.ndarray:
    """
    Apply tone curve adjustment.
    
    Args:
        image: Image array (0-1 float range)
        curve_points: List of (x, y) points defining the curve
                     Points should be in range (0, 1)
                     
    Returns:
        np.ndarray: Adjusted image
    """
    if not curve_points or len(curve_points) < 2:
        return image.copy()
    
    # Create interpolation function
    x_points = [p[0] for p in curve_points]
    y_points = [p[1] for p in curve_points]
    
    # Create spline interpolation
    try:
        curve_func = interpolate.interp1d(
            x_points, y_points,
            kind='cubic',
            bounds_error=False,
            fill_value='extrapolate'
        )
    except:
        # Fallback to linear if cubic fails
        curve_func = interpolate.interp1d(
            x_points, y_points,
            kind='linear',
            bounds_error=False,
            fill_value='extrapolate'
        )
    
    # Apply curve
    result = curve_func(image)
    return np.clip(result, 0, 1)


def adjust_highlights_shadows(
    image: np.ndarray,
    highlights: float,
    shadows: float
) -> np.ndarray:
    """
    Adjust highlights and shadows.
    
    Args:
        image: Image array (0-1 float range)
        highlights: Highlights adjustment (-1 to 1)
        shadows: Shadows adjustment (-1 to 1)
        
    Returns:
        np.ndarray: Adjusted image
    """
    result = image.copy()
    
    # Apply highlights adjustment (darken bright areas or brighten)
    if abs(highlights) > 0.01:
        # Create mask for highlights (luminance > 0.5)
        if len(image.shape) == 3 and image.shape[2] == 3:
            luminance = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
        else:
            luminance = image
        
        highlight_mask = np.power(luminance, 0.5)  # Soft mask
        if highlights > 0:
            result = result * (1 - highlight_mask * highlights * 0.3)
        else:
            result = result + (1 - result) * (-highlight_mask * highlights * 0.3)
    
    # Apply shadows adjustment
    if abs(shadows) > 0.01:
        # Create mask for shadows (luminance < 0.5)
        if len(image.shape) == 3 and image.shape[2] == 3:
            luminance = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
        else:
            luminance = image
        
        shadow_mask = np.power(1 - luminance, 0.5)  # Soft mask
        if shadows > 0:
            result = result + (1 - result) * (shadow_mask * shadows * 0.3)
        else:
            result = result * (1 + shadow_mask * shadows * 0.3)
    
    return np.clip(result, 0, 1)
