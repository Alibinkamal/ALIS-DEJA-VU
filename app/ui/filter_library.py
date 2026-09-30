"""Built-in non-AI look library for ALIS DEJA VU.
Looks are deterministic processing recipes, not external LUT/image assets.
"""
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class Look:
    id: str
    name: str
    family: str
    category: str
    accent: str
    recipe: Dict[str, float]
    description: str = ""

_FAMILIES = {
    "Cinematic": [
        ("A1","Noir Cinema",{"contrast":.22,"shadows":-.10,"highlights":-.08,"temperature":-.10,"saturation":-.08}),
        ("A2","Blue Hour",{"contrast":.16,"shadows":-.12,"highlights":-.04,"temperature":-.18,"tint":.04}),
        ("A3","Golden Frame",{"contrast":.18,"highlights":-.08,"temperature":.20,"vibrance":.18}),
        ("B1","Teal Shadow",{"contrast":.25,"shadows":-.16,"temperature":-.16,"tint":.08,"saturation":-.04}),
        ("B2","Amber Light",{"contrast":.18,"highlights":.05,"temperature":.28,"vibrance":.20}),
        ("B3","Midnight",{"contrast":.28,"shadows":-.22,"temperature":-.22,"saturation":-.10}),
        ("AB1","Epic Matte",{"contrast":-.04,"shadows":.10,"highlights":-.12,"saturation":-.14}),
        ("AB2","Cinema Fade",{"contrast":-.12,"shadows":.08,"highlights":-.10,"temperature":.08,"saturation":-.10}),
        ("AB3","Deep Focus",{"contrast":.32,"shadows":-.18,"highlights":-.12,"vibrance":.12}),
    ],
    "Portrait": [
        ("P1","Natural",{"contrast":.03,"highlights":-.08,"shadows":.05,"temperature":.04,"vibrance":.08}),
        ("P2","Soft Skin",{"contrast":-.06,"highlights":-.12,"shadows":.10,"saturation":-.03}),
        ("P3","Warm Portrait",{"contrast":.10,"temperature":.18,"vibrance":.15}),
        ("P4","Editorial",{"contrast":.20,"highlights":-.12,"shadows":-.05,"saturation":-.06}),
        ("P5","Clean Studio",{"contrast":.08,"highlights":-.04,"shadows":.06,"vibrance":.10}),
        ("P6","Golden Skin",{"temperature":.24,"tint":.03,"vibrance":.18,"highlights":-.06}),
        ("P7","Moody Portrait",{"contrast":.22,"shadows":-.15,"saturation":-.08,"temperature":-.04}),
        ("P8","Film Portrait",{"contrast":.08,"highlights":-.10,"shadows":.06,"temperature":.08,"saturation":-.08}),
        ("P9","Luxury Portrait",{"contrast":.16,"highlights":-.05,"temperature":.12,"vibrance":.20}),
        ("P10","Dramatic Portrait",{"contrast":.30,"shadows":-.18,"highlights":-.12,"saturation":-.04}),
    ],
    "Fashion": [
        ("F1","Clean Editorial",{"contrast":.16,"highlights":-.06,"vibrance":.16}),
        ("F2","High Fashion",{"contrast":.28,"shadows":-.12,"saturation":-.12}),
        ("F3","Luxury",{"contrast":.20,"temperature":.10,"vibrance":.22}),
        ("F4","Cool Editorial",{"contrast":.16,"temperature":-.18,"tint":.04}),
        ("F5","Warm Editorial",{"contrast":.14,"temperature":.22,"vibrance":.12}),
        ("F6","Matte Fashion",{"contrast":-.10,"shadows":.12,"highlights":-.10,"saturation":-.10}),
        ("F7","Contrast Fashion",{"contrast":.34,"shadows":-.18,"highlights":-.10}),
        ("F8","Night Fashion",{"contrast":.30,"shadows":-.20,"temperature":-.18,"saturation":-.10}),
        ("F9","Magazine",{"contrast":.18,"brightness":.03,"vibrance":.20}),
        ("F10","Runway",{"contrast":.26,"temperature":-.06,"saturation":-.14}),
    ],
    "Film": [
        ("A1","35mm Warm",{"contrast":.08,"temperature":.14,"saturation":-.05}),
        ("A2","35mm Cool",{"contrast":.10,"temperature":-.14,"saturation":-.06}),
        ("A3","Classic Print",{"contrast":-.04,"highlights":-.10,"shadows":.08,"saturation":-.12}),
        ("B1","Kodak Mood",{"contrast":.12,"temperature":.12,"vibrance":.16}),
        ("B2","Portra Soft",{"contrast":-.08,"highlights":-.12,"shadows":.10,"temperature":.08}),
        ("B3","Ektar Pop",{"contrast":.24,"saturation":.08,"vibrance":.20}),
        ("C1","Faded Negative",{"contrast":-.14,"shadows":.14,"highlights":-.14,"saturation":-.18}),
        ("C2","Old Stock",{"contrast":-.08,"temperature":.20,"saturation":-.16}),
        ("C3","Green Cast",{"contrast":.06,"temperature":-.08,"tint":-.12,"saturation":-.08}),
    ],
    "Vintage": [
        ("V1","Sepia Dust",{"contrast":-.05,"temperature":.30,"saturation":-.22}),
        ("V2","Old Album",{"contrast":-.12,"shadows":.12,"highlights":-.16,"temperature":.18}),
        ("V3","Polaroid",{"contrast":-.10,"brightness":.04,"saturation":-.06,"temperature":.10}),
        ("V4","Retro Pop",{"contrast":.16,"saturation":.14,"temperature":.08}),
        ("V5","Dusty Blue",{"contrast":-.04,"temperature":-.20,"saturation":-.12}),
        ("V6","Faded Rose",{"contrast":-.10,"temperature":.08,"tint":.14,"saturation":-.10}),
    ],
    "Moody": [
        ("M1","Low Key",{"contrast":.28,"shadows":-.24,"highlights":-.08,"saturation":-.10}),
        ("M2","Rainy Night",{"contrast":.20,"shadows":-.20,"temperature":-.20,"saturation":-.12}),
        ("M3","Velvet",{"contrast":.16,"shadows":-.10,"temperature":.06,"vibrance":.12}),
        ("M4","Dark Olive",{"contrast":.22,"shadows":-.16,"temperature":-.04,"tint":-.10}),
        ("M5","Blue Smoke",{"contrast":.26,"shadows":-.20,"temperature":-.24}),
        ("M6","Black Fashion",{"contrast":.34,"shadows":-.28,"highlights":-.12,"saturation":-.18}),
    ],
    "Warm": [
        ("W1","Sunset",{"temperature":.30,"vibrance":.18,"highlights":-.08}),
        ("W2","Honey",{"temperature":.24,"tint":.02,"saturation":.06}),
        ("W3","Peach",{"temperature":.18,"tint":.12,"vibrance":.12}),
        ("W4","Candle",{"temperature":.34,"contrast":.08,"highlights":-.14}),
        ("W5","Desert",{"temperature":.22,"contrast":.18,"saturation":-.06}),
    ],
    "Cool": [
        ("C1","Arctic",{"temperature":-.34,"contrast":.12,"saturation":-.08}),
        ("C2","Steel",{"temperature":-.22,"contrast":.24,"tint":-.04}),
        ("C3","Ocean",{"temperature":-.20,"vibrance":.18,"saturation":-.02}),
        ("C4","Moonlight",{"temperature":-.30,"contrast":.20,"shadows":-.12}),
        ("C5","Ice Editorial",{"temperature":-.26,"contrast":.18,"highlights":.04}),
    ],
    "B&W": [
        ("BW1","Classic",{"saturation":-1.0,"contrast":.12}),
        ("BW2","Silver",{"saturation":-1.0,"contrast":.24,"highlights":-.08}),
        ("BW3","Soft Mono",{"saturation":-1.0,"contrast":-.10,"shadows":.10}),
        ("BW4","High Contrast",{"saturation":-1.0,"contrast":.42,"shadows":-.20}),
        ("BW5","Matte Mono",{"saturation":-1.0,"contrast":-.14,"shadows":.12,"highlights":-.12}),
    ],
    "Editorial": [
        ("E1","Minimal",{"contrast":.08,"saturation":-.12,"vibrance":.08}),
        ("E2","Paper",{"contrast":-.08,"brightness":.04,"saturation":-.10}),
        ("E3","Gallery",{"contrast":.18,"highlights":-.10,"shadows":.08}),
        ("E4","Monument",{"contrast":.30,"saturation":-.16,"temperature":-.06}),
        ("E5","Soft Flash",{"contrast":.04,"brightness":.06,"highlights":-.14,"vibrance":.14}),
    ],
    "Night": [
        ("N1","Neon",{"contrast":.28,"temperature":-.16,"vibrance":.28}),
        ("N2","City Rain",{"contrast":.24,"shadows":-.20,"temperature":-.18}),
        ("N3","After Dark",{"contrast":.34,"shadows":-.26,"saturation":-.08}),
        ("N4","Street Blue",{"contrast":.26,"temperature":-.28,"vibrance":.16}),
        ("N5","Neon Amber",{"contrast":.24,"temperature":.20,"vibrance":.24}),
    ],
    "Clean": [
        ("CL1","True Color",{"contrast":.02,"vibrance":.10}),
        ("CL2","Bright",{"brightness":.10,"highlights":-.06,"vibrance":.14}),
        ("CL3","Crisp",{"contrast":.14,"vibrance":.14}),
        ("CL4","Airy",{"contrast":-.06,"brightness":.08,"shadows":.12,"saturation":-.03}),
        ("CL5","Fresh",{"contrast":.06,"temperature":.04,"vibrance":.18}),
    ],
}

_COLORS=["#8B5CF6","#06B6D4","#F59E0B","#EC4899","#22C55E","#EF4444","#3B82F6","#14B8A6","#F97316","#A855F7"]

def _build() -> List[Look]:
    out=[]
    for ci,(category,items) in enumerate(_FAMILIES.items()):
        for i,(code,name,recipe) in enumerate(items):
            out.append(Look(f"{category.lower().replace(' ','-')}-{code}",name,category,category,_COLORS[(ci+i)%len(_COLORS)],recipe))
    return out

LOOKS=_build()
LOOKS_BY_ID={x.id:x for x in LOOKS}
CATEGORIES=list(_FAMILIES.keys())

def get_looks(category=None):
    return [x for x in LOOKS if category is None or x.category==category]

def get_look(look_id):
    return LOOKS_BY_ID[look_id]
