import tempfile,unittest
from pathlib import Path
import numpy as np
from app.core import LayerStack,Mask,BlendMode
from app.presets import PresetManager
from app.project import ProjectFile
from app.export import export_image

class TestPhase6(unittest.TestCase):
    def test_project_roundtrip_and_preset(self):
        image=np.full((12,16,3),.4,np.float32); stack=LayerStack(image); layer=stack.add("Retouch");layer.pixels[:]=.6;layer.mask.paint(8,6,3,1)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"test.alis"
            ProjectFile.save(p,"portrait.jpg",{"exposure":.2},stack)
            manifest,loaded=ProjectFile.load(p,LayerStack,Mask,BlendMode)
            self.assertEqual(manifest["format"],"ALIS-DEJA-VU");self.assertEqual(len(loaded.layers),2)
            pm=PresetManager(Path(td)/"presets");pm.save("Custom",{"adjustments":{"exposure":.2}});self.assertIn("Custom",pm.list_names())
            out=Path(td)/"out.jpg";export_image(image,out,quality=90);self.assertTrue(out.exists())

if __name__=="__main__":unittest.main()
