"""
ImageLoader - Load images from disk in various formats
"""

from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image

try:
    import rawpy
    HAS_RAWPY = True
except ImportError:
    HAS_RAWPY = False

from app.image.formats import STANDARD_FORMATS, RAW_FORMATS


class ImageLoader:
    """
    Load images from various formats including RAW if available.
    """
    
    @staticmethod
    def can_load(file_path: str) -> bool:
        """
        Check if file format is supported.
        
        Args:
            file_path: Path to image file
            
        Returns:
            bool: True if format is supported
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix in STANDARD_FORMATS:
            return True
        
        if suffix in RAW_FORMATS and HAS_RAWPY:
            return True
        
        return False
    
    @staticmethod
    def load(file_path: str) -> np.ndarray:
        """
        Load image from file.
        
        Args:
            file_path: Path to image file
            
        Returns:
            np.ndarray: Image data (0-1 float range, RGB)
            
        Raises:
            IOError: If file cannot be loaded
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        # Try standard formats first
        if suffix in STANDARD_FORMATS:
            return ImageLoader._load_standard(file_path)
        
        # Try RAW formats
        if suffix in RAW_FORMATS and HAS_RAWPY:
            return ImageLoader._load_raw(file_path)
        
        raise IOError(f"Unsupported image format: {suffix}")
    
    @staticmethod
    def _load_standard(file_path: str) -> np.ndarray:
        """
        Load standard format (JPEG, PNG, TIFF).
        
        Args:
            file_path: Path to image file
            
        Returns:
            np.ndarray: Image data (0-1 float range, RGB)
        """
        try:
            pil_image = Image.open(file_path)
            
            # Convert to RGB
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                if pil_image.mode == 'RGBA':
                    background.paste(pil_image, mask=pil_image.split()[3])
                else:
                    background.paste(pil_image)
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array (0-1 float range)
            image_array = np.array(pil_image).astype(np.float32) / 255.0
            return image_array
            
        except Exception as e:
            raise IOError(f"Failed to load standard image '{file_path}': {str(e)}")
    
    @staticmethod
    def _load_raw(file_path: str) -> np.ndarray:
        """
        Load RAW image using rawpy.
        
        Args:
            file_path: Path to RAW file
            
        Returns:
            np.ndarray: Image data (0-1 float range, RGB)
        """
        if not HAS_RAWPY:
            raise IOError("RAW support not available. Install 'rawpy' package.")
        
        try:
            with rawpy.imread(file_path) as raw:
                # Use postprocess for quick preview
                # For production, might want more control
                rgb_image = raw.postprocess()
            
            # Convert to 0-1 float range
            image_array = rgb_image.astype(np.float32) / 255.0
            return image_array
            
        except Exception as e:
            raise IOError(f"Failed to load RAW image '{file_path}': {str(e)}")
    
    @staticmethod
    def get_supported_extensions() -> list:
        """
        Get list of supported file extensions.
        
        Returns:
            list: File extensions (with dot)
        """
        extensions = list(STANDARD_FORMATS.keys())
        if HAS_RAWPY:
            extensions.extend(RAW_FORMATS.keys())
        return extensions
