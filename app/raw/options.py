from dataclasses import dataclass
@dataclass
class RawOptions:
    use_camera_wb: bool=True
    use_auto_wb: bool=False
    half_size: bool=False
    no_auto_bright: bool=False
    output_bps: int=16
