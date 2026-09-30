"""
ImageData - Core image data structure for non-destructive editing

Represents an image with:
- Original raw image data
- Working copy for editing
- Layers
- Adjustments state
"""

import numpy as np
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image


class ImageData:
    """
    Represents an image with support for non-destructive editing.
    
    Maintains:
    - Original image (unchanged)
    - Working image (for preview)
    - Metadata
    - Adjustment state
    """
    
    def __init__(self, file_path: str):
        """
        Initialize ImageData from a file path.
        
        Args:
            file_path: Path to image file
        """
        self.file_path = Path(file_path)
        self.original_image = None
        self.working_image = None
        self.layers = []
        self.adjustments = {}
        
        self._load_image()
    
    def _load_image(self) -> None:
        """Load image from file path"""
        try:
            # Load with PIL for compatibility
            pil_image = Image.open(self.file_path)
            
            # Convert RGBA to RGB if needed
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                background.paste(pil_image, mask=pil_image.split()[-1] if pil_image.mode == 'RGBA' else None)
                pil_image = background
            elif pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array (0-1 float range for processing)
            self.original_image = np.array(pil_image).astype(np.float32) / 255.0
            self.working_image = self.original_image.copy()
            
        except Exception as e:
            raise IOError(f"Failed to load image '{self.file_path}': {str(e)}")
    
    def get_working_image(self) -> np.ndarray:
        """
        Get current working image (0-1 float range).
        
        Returns:
            np.ndarray: Working image data
        """
        return self.working_image
    
    def get_display_image(self) -> np.ndarray:
        """
        Get image in 0-255 uint8 format for display.
        
        Returns:
            np.ndarray: Image suitable for display (0-255 uint8)
        """
        return np.clip(self.working_image * 255, 0, 255).astype(np.uint8)
    
    def reset_to_original(self) -> None:
        """Reset working image to original"""
        self.working_image = self.original_image.copy()
        self.adjustments = {}
    
    def update_working_image(self, data: np.ndarray) -> None:
        """
        Update working image.
        
        Args:
            data: New image data (should be 0-1 float range)
        """
        self.working_image = np.clip(data, 0, 1)
    
    def get_dimensions(self) -> Tuple[int, int]:
        """
        Get image dimensions (width, height).
        
        Returns:
            Tuple[int, int]: (width, height)
        """
        if self.original_image is None:
            return (0, 0)
        height, width = self.original_image.shape[:2]
        return (width, height)
    
    def set_adjustment(self, name: str, value: float) -> None:
        """
        Store adjustment parameter.
        
        Args:
            name: Adjustment name (e.g., 'exposure', 'contrast')
            value: Adjustment value
        """
        self.adjustments[name] = value
    
    def get_adjustment(self, name: str, default: float = 0.0) -> float:
        """
        Get adjustment parameter.
        
        Args:
            name: Adjustment name
            default: Default value if not set
            
        Returns:
            float: Adjustment value
        """
        return self.adjustments.get(name, default)
    
    def get_filename(self) -> str:
        """Get image filename"""
        return self.file_path.name
    
    def get_filepath(self) -> str:
        """Get full image file path"""
        return str(self.file_path)
