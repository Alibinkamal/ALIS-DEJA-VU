from pathlib import Path
import numpy as np
from PIL import Image
try:
    import rawpy
    HAS_RAWPY=True
except ImportError:
    HAS_RAWPY=False
from .formats import STANDARD_FORMATS,RAW_FORMATS
from app.raw import RawOptions

class ImageLoader:
    @staticmethod
    def can_load(path):
        s=Path(path).suffix.lower()
        return s in STANDARD_FORMATS or (s in RAW_FORMATS and HAS_RAWPY)
    @staticmethod
    def load(path,raw_options=None):
        s=Path(path).suffix.lower()
        if s in STANDARD_FORMATS:
            with Image.open(path) as im:
                return np.asarray(im.convert("RGB"),np.float32)/255
        if s in RAW_FORMATS and HAS_RAWPY:
            opts=raw_options or RawOptions()
            with rawpy.imread(path) as raw:
                arr=raw.postprocess(
                    use_camera_wb=opts.use_camera_wb,
                    use_auto_wb=opts.use_auto_wb,
                    half_size=opts.half_size,
                    no_auto_bright=opts.no_auto_bright,
                    output_bps=opts.output_bps)
            return arr.astype(np.float32)/float((1<<opts.output_bps)-1)
        if s in RAW_FORMATS:
            raise IOError("RAW support requires the optional rawpy package")
        raise IOError(f"Unsupported image format: {s}")
    @staticmethod
    def get_supported_extensions():
        return list(STANDARD_FORMATS)+([] if not HAS_RAWPY else list(RAW_FORMATS))
