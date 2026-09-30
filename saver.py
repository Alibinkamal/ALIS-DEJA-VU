"""
ImageSaver - Save/Export images to disk
"""

from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image

from app.image.formats import EXPORT_FORMATS


class ImageSaver:
    """
    Save images to disk in various formats with quality control.
    """
    
    @staticmethod
    def save(
        image_data: np.ndarray,
        file_path: str,
        quality: int = 95,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Save image to file.
        
        Args:
            image_data: Image array (0-1 float range)
            file_path: Output file path
            quality: JPEG quality (1-100)
            metadata: Optional metadata dictionary
            
        Raises:
            IOError: If save fails
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix not in EXPORT_FORMATS:
            raise IOError(f"Unsupported export format: {suffix}")
        
        try:
            # Convert to PIL Image
            pil_image = ImageSaver._array_to_pil(image_data)
            
            # Determine save format
            fmt = EXPORT_FORMATS[suffix]
            
            # Save with appropriate quality settings
            if fmt == 'JPEG':
                pil_image.save(
                    file_path,
                    format='JPEG',
                    quality=quality,
                    optimize=True
                )
            elif fmt == 'PNG':
                pil_image.save(
                    file_path,
                    format='PNG',
                    optimize=True
                )
            elif fmt == 'TIFF':
                pil_image.save(
                    file_path,
                    format='TIFF'
                )
            else:
                pil_image.save(file_path)
                
        except Exception as e:
            raise IOError(f"Failed to save image '{file_path}': {str(e)}")
    
    @staticmethod
    def _array_to_pil(image_data: np.ndarray) -> Image.Image:
        """
        Convert numpy array to PIL Image.
        
        Args:
            image_data: Image array (0-1 float range)
            
        Returns:
            Image.Image: PIL Image object
        """
        # Ensure 0-255 range
        uint8_data = np.clip(image_data * 255, 0, 255).astype(np.uint8)
        
        # Handle different array shapes
        if len(uint8_data.shape) == 2:
            # Grayscale
            return Image.fromarray(uint8_data, mode='L')
        elif uint8_data.shape[2] == 3:
            # RGB
            return Image.fromarray(uint8_data, mode='RGB')
        elif uint8_data.shape[2] == 4:
            # RGBA
            return Image.fromarray(uint8_data, mode='RGBA')
        else:
            raise ValueError(f"Unsupported image shape: {uint8_data.shape}")
