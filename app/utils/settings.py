from pathlib import Path
import json
class AppSettings:
    DEFAULTS={"language":"English","theme":"Dark","autosave":True,"preview_quality":"Balanced","worker_threads":2,"cache_items":8,"default_jpeg_quality":95}
    def __init__(self,path=None):
        self.path=Path(path or Path.home()/".alis_deja_vu"/"settings.json");self.path.parent.mkdir(parents=True,exist_ok=True);self.data=self.DEFAULTS.copy();self.load()
    def load(self):
        if self.path.exists():
            try:self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
            except Exception:pass
        return self.data
    def save(self): self.path.write_text(json.dumps(self.data,indent=2,ensure_ascii=False),encoding="utf-8")
    def get(self,key,default=None): return self.data.get(key,default)
    def set(self,key,value): self.data[key]=value
