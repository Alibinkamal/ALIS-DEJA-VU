from pathlib import Path
import json
from dataclasses import dataclass,asdict

BUILTIN_PRESETS={
"Editorial Clean":{"adjustments":{"exposure":0.05,"contrast":0.08,"saturation":-0.03},"detail":{"clarity":0.08,"sharpen":0.2}},
"Fashion Neutral":{"adjustments":{"exposure":0.0,"contrast":0.12,"saturation":-0.04},"detail":{"clarity":0.05}},
"Studio Beauty":{"adjustments":{"exposure":0.08,"contrast":-0.03,"saturation":-0.02},"skin":{"smooth":0.18}},
"Warm Skin":{"adjustments":{"temperature":0.18,"saturation":0.02},"color":{"shadows":[0.01,0.0,-0.01],"highlights":[0.03,0.015,0.0]}},
"Cinematic Portrait":{"adjustments":{"contrast":0.10,"saturation":-0.05},"color":{"shadows":[-0.01,0.0,0.03],"highlights":[0.03,0.02,-0.01]},"grain":{"amount":0.018}},
"Soft Contrast":{"adjustments":{"contrast":-0.12,"brightness":0.03}},
"Film Inspired":{"adjustments":{"contrast":0.06,"saturation":-0.03},"grain":{"amount":0.025,"size":1.2}},
"Cool Shadows / Warm Highlights":{"color":{"shadows":[-0.02,0.0,0.04],"highlights":[0.04,0.02,-0.01],"amount":0.22}}
}

class PresetManager:
    def __init__(self,directory=None):
        self.directory=Path(directory or Path.home()/".alis_deja_vu"/"presets"); self.directory.mkdir(parents=True,exist_ok=True)
    def list_names(self):
        return list(BUILTIN_PRESETS)+sorted(p.stem for p in self.directory.glob("*.json"))
    def get(self,name):
        if name in BUILTIN_PRESETS:return BUILTIN_PRESETS[name]
        p=self.directory/(name+".json")
        if not p.exists(): raise FileNotFoundError(name)
        return json.loads(p.read_text(encoding="utf-8"))
    def save(self,name,data):
        if not name.strip(): raise ValueError("Preset name is required")
        payload={"format":1,"name":name.strip(),"settings":data}
        p=self.directory/(name.strip().replace("/","_").replace("\","_")+".json")
        p.write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding="utf-8"); return p
    def delete(self,name):
        p=self.directory/(name+".json")
        if p.exists():p.unlink()