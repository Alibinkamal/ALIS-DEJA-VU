import io,json,zipfile
from pathlib import Path
import numpy as np

PROJECT_VERSION=1

class ProjectFile:
    @staticmethod
    def save(path,original_path,adjustments,layers,metadata=None):
        path=Path(path)
        manifest={"format":"ALIS-DEJA-VU","version":PROJECT_VERSION,"original_path":str(original_path),"adjustments":adjustments,"metadata":metadata or {},"layers":[]}
        arrays={}
        for i,layer in enumerate(layers.layers):
            key=f"layer_{i}"
            arrays[key]=layer.pixels.astype(np.float32)
            entry={"name":layer.name,"opacity":layer.opacity,"visible":layer.visible,"blend_mode":layer.blend_mode.value,"locked":layer.locked,"pixels":f"{key}.npy"}
            if layer.mask is not None:
                mk=f"mask_{i}"; arrays[mk]=layer.mask.data.astype(np.float32); entry["mask"]=f"{mk}.npy"
            else: entry["mask"]=None
            manifest["layers"].append(entry)
        with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
            z.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
            for name,arr in arrays.items():
                b=io.BytesIO();np.save(b,arr,allow_pickle=False);z.writestr(name+".npy",b.getvalue())
        return path
    @staticmethod
    def load(path,layer_stack_cls,mask_cls,blend_enum):
        with zipfile.ZipFile(path,"r") as z:
            manifest=json.loads(z.read("manifest.json").decode("utf-8"))
            if manifest.get("format")!="ALIS-DEJA-VU": raise ValueError("Not an ALIS DEJA VU project")
            if int(manifest.get("version",0))>PROJECT_VERSION: raise ValueError("Project was created by a newer version")
            layers_data=manifest["layers"]
            first=np.load(io.BytesIO(z.read(layers_data[0]["pixels"])),allow_pickle=False)
            stack=layer_stack_cls(first); stack.layers=[]
            for e in layers_data:
                pixels=np.load(io.BytesIO(z.read(e["pixels"])),allow_pickle=False).astype(np.float32)
                mask=None
                if e.get("mask"):
                    m=np.load(io.BytesIO(z.read(e["mask"])),allow_pickle=False).astype(np.float32)
                    mask=mask_cls(m.shape[1],m.shape[0]);mask.data=np.clip(m,0,1)
                layer=stack.add(e["name"],pixels)
                layer.opacity=float(e.get("opacity",1));layer.visible=bool(e.get("visible",True));layer.blend_mode=blend_enum(e.get("blend_mode","Normal"));layer.locked=bool(e.get("locked",False));layer.mask=mask
            if stack.layers: stack.active_index=min(len(stack.layers)-1,0)
            return manifest,stack