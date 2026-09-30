import sys,copy
from pathlib import Path
import numpy as np
from PySide6.QtWidgets import (
    QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QFileDialog,QMessageBox,
    QListWidget,QListWidgetItem,QPushButton,QLabel,QComboBox,QSlider,QApplication,QFrame,QToolButton,QScrollArea,QGridLayout,QLineEdit,QStackedWidget,QButtonGroup,QSizePolicy,
    QInputDialog,QDialog,QFormLayout,QDialogButtonBox,QSpinBox,QDoubleSpinBox,QCheckBox
)
from PySide6.QtGui import QKeySequence,QAction,QIcon
from PySide6.QtCore import Qt,QThreadPool
from shiboken6 import isValid
from app import APP_NAME,APP_VERSION
from app.core import ImageData,LayerStack,UndoRedoManager,CallableCommand
from app.core.layers import BlendMode
from app.core.masks import Mask
from app.image import ImageSaver,SUPPORTED_FORMATS_FILTER,EXPORT_FORMATS_FILTER
from app.processing import (
    heal_spot,clone_stamp,dodge_burn,adjust_exposure,adjust_brightness,adjust_contrast,
    adjust_saturation,adjust_temperature,adjust_highlights_shadows,apply_curve,
)
from app.color import apply_curves,apply_hsl,apply_vibrance,color_balance,selective_color,split_tone,apply_cube_lut
from app.retouch import frequency_separation,skin_smooth,skin_tone_correct,make_skin_mask
from app.processing.detail import sharpen,clarity,denoise,add_grain
from app.presets import PresetManager
from app.project import ProjectFile
from app.export import export_image
from app.performance import PreviewCache
from app.ui.filter_library import LOOKS,CATEGORIES,get_look
from app.utils import AppSettings,get_logger
from app.ui.widgets import ImageCanvas,LookCard
from app.ui.theme import StyleSheet,Colors

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}");self.resize(1500,920)
        self.image_data=None;self.layers=None;self.undo=UndoRedoManager(50)
        self.tool="Brush";self.brush_size=40;self.brush_opacity=1.;self.clone_source=None
        self.settings=AppSettings();self.cache=PreviewCache(self.settings.get("cache_items",8));self.logger=get_logger()
        self.thread_pool=QThreadPool.globalInstance();self.thread_pool.setMaxThreadCount(max(1,int(self.settings.get("worker_threads",2))))
        self.preset_manager=PresetManager()
        self.adjustments={"exposure":0.,"brightness":0.,"contrast":0.,"highlights":0.,"shadows":0.,"saturation":0.,"temperature":0.,"tint":0.,"vibrance":0.}
        self.advanced={"curves_master":None,"curves_r":None,"curves_g":None,"curves_b":None,"hsl":{},"balance":None,"selective":None,"split":None,"lut":None}
        self.active_look=None;self.look_intensity=1.0
        self.pro_controls={"whites":0.0,"blacks":0.0,"clarity":0.0,"texture":0.0,"dehaze":0.0,"vignette":0.0,"grain":0.0}
        self._build();self._menus()

    def _build(self):
        root=QWidget();self.setCentralWidget(root);outer=QVBoxLayout(root);outer.setContentsMargins(10,10,10,8);outer.setSpacing(8)
        top=QFrame();top.setObjectName("TopBar");tl=QHBoxLayout(top);tl.setContentsMargins(14,8,14,8)
        brand=QLabel("ALIS DEJA VU");brand.setObjectName("Brand");tl.addWidget(brand);ver=QLabel(f"  v{APP_VERSION}");ver.setObjectName("Subtle");tl.addWidget(ver);tl.addStretch()
        self.nav_group=QButtonGroup(self);self.nav_group.setExclusive(True)
        for name,label in [("looks","LOOKS"),("adjust","ADJUST"),("retouch","RETOUCH"),("layers","LAYERS")]:
            b=QToolButton();b.setObjectName("Nav");b.setText(label);b.setCheckable(True);b.clicked.connect(lambda checked,n=name:self.switch_section(n));self.nav_group.addButton(b);tl.addWidget(b);setattr(self,name+"_nav",b)
        self.looks_nav.setChecked(True);outer.addWidget(top)
        body=QHBoxLayout();body.setContentsMargins(0,0,0,0);body.setSpacing(8);outer.addLayout(body,1)
        left=QFrame();left.setObjectName("SidePanel");left.setFixedWidth(178);ll=QVBoxLayout(left);ll.setContentsMargins(10,12,10,12)
        title=QLabel("WORKSPACE");title.setObjectName("SectionTitle");ll.addWidget(title)
        for text,name in [("Open Image","open"),("Open Project","open_project"),("Save Project","save"),("Export","export")]:
            b=QPushButton(text);b.clicked.connect({"open":self.open_image,"open_project":self.open_project,"save":self.save_project,"export":self.export}[name]);ll.addWidget(b)
        ll.addSpacing(10);lab=QLabel("TOOLS");lab.setObjectName("Subtle");ll.addWidget(lab)
        self.tool_buttons={}
        for name in ["Brush","Mask Paint","Eraser","Healing","Clone","Dodge","Burn"]:
            b=QPushButton(name);b.clicked.connect(lambda _,n=name:self.set_tool(n));ll.addWidget(b);self.tool_buttons[name]=b
        ll.addStretch();self.info=QLabel("Open an image to begin.");self.info.setObjectName("Subtle");self.info.setWordWrap(True);ll.addWidget(self.info);body.addWidget(left)
        center=QFrame();center.setObjectName("Section");cl=QVBoxLayout(center);cl.setContentsMargins(4,4,4,4);cl.setSpacing(4)
        self.canvas=ImageCanvas();self.canvas.stroke.connect(self.stroke);self.canvas.file_dropped.connect(self.load_image);cl.addWidget(self.canvas,1)
        bottom=QHBoxLayout()
        for text,fn in [("Fit",self.canvas.fit_to_window),("100%",self.canvas.actual_size),("−",self.canvas.zoom_out),("+",self.canvas.zoom_in),("Before/After",lambda:self.canvas.set_before_after(not self.canvas.show_original))]:
            b=QPushButton(text);b.clicked.connect(fn);bottom.addWidget(b)
        bottom.addStretch();self.status_hint=QLabel("Ready");self.status_hint.setObjectName("Subtle");bottom.addWidget(self.status_hint);cl.addLayout(bottom);body.addWidget(center,1)
        self.stack=QStackedWidget();self.stack.setObjectName("Inspector");self.stack.setFixedWidth(390);body.addWidget(self.stack)
        self._build_looks_page();self._build_adjust_page();self._build_retouch_page();self._build_layers_page()
        self.statusBar().showMessage("Ready — open an image to begin");self.setStyleSheet(StyleSheet.get_stylesheet())

    def _page(self,title):
        page=QFrame();page.setObjectName("Inspector");lay=QVBoxLayout(page);lay.setContentsMargins(12,12,12,12);lay.setSpacing(8);lab=QLabel(title);lab.setObjectName("SectionTitle");lay.addWidget(lab);return page,lay

    def _build_looks_page(self):
        page,lay=self._page("LOOK LIBRARY");self.look_search=QLineEdit();self.look_search.setPlaceholderText("Search looks…  A1, B2, Portrait, Film");self.look_search.textChanged.connect(self._refresh_look_cards);lay.addWidget(self.look_search)
        cats=QScrollArea();cats.setWidgetResizable(True);cw=QWidget();cly=QHBoxLayout(cw);cly.setContentsMargins(0,0,0,0);self.category_group=QButtonGroup(self);self.category_group.setExclusive(True)
        for cat in ["ALL"]+CATEGORIES:
            b=QToolButton();b.setText(cat);b.setCheckable(True);b.clicked.connect(lambda _,c=cat:self._set_category(c));self.category_group.addButton(b);cly.addWidget(b)
        cly.addStretch();cats.setWidget(cw);cats.setFixedHeight(46);lay.addWidget(cats)
        self.look_scroll=QScrollArea();self.look_scroll.setWidgetResizable(True);self.look_container=QWidget();self.look_grid=QGridLayout(self.look_container);self.look_grid.setContentsMargins(2,2,2,2);self.look_grid.setSpacing(8);self.look_scroll.setWidget(self.look_container);lay.addWidget(self.look_scroll,1)
        controls=QFrame();controls.setObjectName("Section");rl=QVBoxLayout(controls);self.look_name=QLabel("No look selected");self.look_name.setObjectName("Subtle");rl.addWidget(self.look_name)
        row=QHBoxLayout();row.addWidget(QLabel("Intensity"));self.look_intensity_slider=QSlider(Qt.Horizontal);self.look_intensity_slider.setRange(0,100);self.look_intensity_slider.setValue(100);self.look_intensity_slider.valueChanged.connect(self._set_look_intensity);row.addWidget(self.look_intensity_slider);self.look_intensity_value=QLabel("100%");row.addWidget(self.look_intensity_value);rl.addLayout(row)
        self.apply_look_btn=QPushButton("Apply Look");self.apply_look_btn.setObjectName("Primary");self.apply_look_btn.clicked.connect(self._apply_selected_look);rl.addWidget(self.apply_look_btn);lay.addWidget(controls);self.stack.addWidget(page);self._set_category("ALL")

    def _build_adjust_page(self):
        page,lay=self._page("PRO EDIT");scroll=QScrollArea();scroll.setWidgetResizable(True);inner=QWidget();il=QVBoxLayout(inner);groups=[("LIGHT",[("exposure",-2,2),("brightness",-1,1),("contrast",-1,1),("highlights",-1,1),("shadows",-1,1),("whites",-1,1),("blacks",-1,1)]),("COLOR",[("temperature",-1,1),("tint",-1,1),("vibrance",-1,1),("saturation",-1,1)]),("EFFECTS",[("clarity",-1,1),("texture",-1,1),("dehaze",-1,1),("vignette",-1,1),("grain",0,.12)])]
        self.pro_sliders={}
        for group,items in groups:
            box=QFrame();box.setObjectName("Section");bl=QVBoxLayout(box);lab=QLabel(group);lab.setObjectName("SectionTitle");bl.addWidget(lab)
            for name,lo,hi in items:
                row=QHBoxLayout();row.addWidget(QLabel(name.title()));sl=QSlider(Qt.Horizontal);sl.setRange(0,1000);sl.setValue(500 if lo<0 else 0);sl.valueChanged.connect(lambda v,n=name,a=lo,b=hi:self._set_pro(n,a+(b-a)*v/1000));row.addWidget(sl);val=QLabel("0");val.setFixedWidth(42);row.addWidget(val);self.pro_sliders[name]=(sl,val,lo,hi);bl.addLayout(row)
            il.addWidget(box)
        advanced=QPushButton("RGB Curves • HSL • Color Balance • LUT");advanced.clicked.connect(self.curves_dialog);il.addWidget(advanced);il.addStretch();scroll.setWidget(inner);lay.addWidget(scroll,1);self.stack.addWidget(page);self.adjust_sliders={k:v[0] for k,v in self.pro_sliders.items() if k in self.adjustments}

    def _build_retouch_page(self):
        page,lay=self._page("RETOUCH & DETAIL")
        for label,fn in [("Frequency Separation",self.frequency_separation_action),("Skin Smoothing",self.skin_smoothing_action),("Skin Tone Balance",self.skin_tone_action),("Sharpen",lambda:self.detail_action("sharpen")),("Clarity",lambda:self.detail_action("clarity")),("Denoise",lambda:self.detail_action("denoise")),("Film Grain",lambda:self.detail_action("grain"))]:
            b=QPushButton(label);b.clicked.connect(fn);lay.addWidget(b)
        lay.addWidget(QLabel("Brush Size"));self.size=QSlider(Qt.Horizontal,page);self.size.setRange(2,400);self.size.setValue(40);self.size.valueChanged.connect(lambda v:setattr(self,"brush_size",v));lay.addWidget(self.size);lay.addWidget(QLabel("Opacity / Flow"));self.opacity=QSlider(Qt.Horizontal,page);self.opacity.setRange(1,100);self.opacity.setValue(100);self.opacity.valueChanged.connect(lambda v:setattr(self,"brush_opacity",v/100));lay.addWidget(self.opacity);b=QPushButton("Invert Active Mask");b.clicked.connect(self.invert_mask);lay.addWidget(b);lay.addStretch();self.stack.addWidget(page)

    def _build_layers_page(self):
        page,lay=self._page("LAYERS");self.layer_list=QListWidget();self.layer_list.currentRowChanged.connect(self.select_layer);lay.addWidget(self.layer_list,1);grid=QGridLayout()
        for i,(text,fn) in enumerate([("＋ Layer",self.add_layer),("Duplicate",self.duplicate_layer),("Delete",self.delete_layer),("↑ Up",lambda:self.move_layer(-1)),("↓ Down",lambda:self.move_layer(1)),("Add Mask",self.add_mask)]):
            b=QPushButton(text);b.clicked.connect(fn);grid.addWidget(b,i//2,i%2)
        lay.addLayout(grid);lay.addWidget(QLabel("Blend Mode"));self.blend=QComboBox();self.blend.addItems([x.value for x in BlendMode]);self.blend.currentTextChanged.connect(self.set_blend);lay.addWidget(self.blend);lay.addWidget(QLabel("Layer Opacity"));self.layer_opacity=QSlider(Qt.Horizontal,page);self.layer_opacity.setRange(0,100);self.layer_opacity.setValue(100);self.layer_opacity.valueChanged.connect(self.set_layer_opacity);lay.addWidget(self.layer_opacity);self.histogram_label=QLabel("Histogram • no image");self.histogram_label.setObjectName("Subtle");self.histogram_label.setWordWrap(True);lay.addWidget(self.histogram_label);self.stack.addWidget(page)

    def switch_section(self,name): self.stack.setCurrentIndex({"looks":0,"adjust":1,"retouch":2,"layers":3}[name])
    def _set_category(self,cat): self.active_category=cat;self._refresh_look_cards()
    def _refresh_look_cards(self):
        while self.look_grid.count():
            item=self.look_grid.takeAt(0)
            if item.widget():item.widget().deleteLater()
        q=self.look_search.text().strip().lower();cat=getattr(self,"active_category","ALL");items=[x for x in LOOKS if (cat=="ALL" or x.category==cat) and (not q or q in x.name.lower() or q in x.id.lower() or q in x.category.lower())]
        for i,look in enumerate(items):
            card=LookCard(look);card.clicked.connect(self._select_look);self.look_grid.addWidget(card,i//2,i%2)
        self.look_grid.setColumnStretch(0,1);self.look_grid.setColumnStretch(1,1)
    def _select_look(self,look_id):
        self.active_look=get_look(look_id);self.look_name.setText(f"{self.active_look.id.split('-')[-1]}  •  {self.active_look.name}");self.look_intensity_slider.setValue(round(self.look_intensity*100));self._apply_selected_look()
    def _set_look_intensity(self,v):
        self.look_intensity=v/100;self.look_intensity_value.setText(f"{v}%")
        if self.active_look:self.render()
    def _apply_selected_look(self):
        if self.active_look:self.look_intensity=self.look_intensity_slider.value()/100;self.render();self.info.setText(f"Look applied: {self.active_look.name} • {round(self.look_intensity*100)}%")
    def _set_pro(self,name,value):
        self.pro_controls[name]=float(value)
        if name in self.adjustments:self.adjustments[name]=float(value)
        if name in self.pro_sliders:self.pro_sliders[name][1].setText(f"{value:.2f}")
        self.render()

    def _menus(self):
        m=self.menuBar()
        f=m.addMenu("File");a=f.addAction("Open Image");a.setShortcut(QKeySequence.Open);a.triggered.connect(self.open_image)
        a=f.addAction("Open Project");a.triggered.connect(self.open_project);a=f.addAction("Save Project");a.setShortcut(QKeySequence.Save);a.triggered.connect(self.save_project)
        a=f.addAction("Export As");a.setShortcut(QKeySequence.SaveAs);a.triggered.connect(self.export)
        f.addSeparator();f.addAction("Exit",self.close)
        e=m.addMenu("Edit");u=e.addAction("Undo");u.setShortcut(QKeySequence.Undo);u.triggered.connect(self.do_undo);r=e.addAction("Redo");r.setShortcut(QKeySequence.Redo);r.triggered.connect(self.do_redo);e.addSeparator();e.addAction("Reset All",self.reset)
        v=m.addMenu("View");v.addAction("Fit",self.canvas.fit_to_window);v.addAction("100%",self.canvas.actual_size);v.addAction("Zoom In",self.canvas.zoom_in);v.addAction("Zoom Out",self.canvas.zoom_out);v.addAction("Before / Original",lambda:self.canvas.set_before_after(True));v.addAction("After / Edited",lambda:self.canvas.set_before_after(False))
        c=m.addMenu("Color")
        c.addAction("RGB Curves",self.curves_dialog);c.addAction("HSL",self.hsl_dialog);c.addAction("Color Balance",self.color_balance_dialog);c.addAction("Selective Color",self.selective_color_dialog);c.addAction("Split Toning",self.split_tone_dialog);c.addAction("Load .cube LUT",self.load_lut);c.addAction("Vibrance +25%",lambda:self.quick_vibrance(.25))
        p=m.addMenu("Presets");p.addAction("Apply Preset",self.apply_preset_dialog);p.addAction("Save Current Preset",self.save_preset);p.addAction("Open Preset Folder",self.open_preset_folder)
        t=m.addMenu("Tools");t.addAction("Frequency Separation",self.frequency_separation_action);t.addAction("Skin Smoothing",self.skin_smoothing_action);t.addAction("Skin Tone Balance",self.skin_tone_action);t.addAction("Sharpen",lambda:self.detail_action("sharpen"));t.addAction("Denoise",lambda:self.detail_action("denoise"));t.addAction("Film Grain",lambda:self.detail_action("grain"))
        s=m.addMenu("Settings");s.addAction("Application Settings",self.settings_dialog);s.addAction("Clear Preview Cache",self.clear_cache)
        self.shortcut_before=QAction(self);self.shortcut_before.setShortcut(QKeySequence("Tab"));self.shortcut_before.triggered.connect(lambda:self.canvas.set_before_after(not self.canvas.show_original));self.addAction(self.shortcut_before)

    def set_tool(self,t):
        self.tool=t;self.clone_source=None
        self.info.setText(f"Active tool: {t}. "+("Alt+click chooses the Clone source." if t=="Clone" else "Paint directly on the canvas."))

    def open_image(self):
        p,_=QFileDialog.getOpenFileName(self,"Open Image","",SUPPORTED_FORMATS_FILTER)
        if p:self.load_image(p)

    def load_image(self,p):
        try:
            self.image_data=ImageData(p);self.layers=LayerStack(self.image_data.original_image);self.undo.clear();self.cache.clear()
            self.adjustments={k:0. for k in self.adjustments};self.pro_controls={k:0. for k in self.pro_controls};self.active_look=None;self.look_intensity=1.0;self.advanced={"curves_master":None,"curves_r":None,"curves_g":None,"curves_b":None,"hsl":{},"balance":None,"selective":None,"split":None,"lut":None}
            for s in self.adjust_sliders.values():
                if isValid(s):
                    s.blockSignals(True);s.setValue(500);s.blockSignals(False)
            self.refresh_layers();self.render();self.canvas.set_before_after(False);self.canvas.fit_to_window()
            self.setWindowTitle(f"{APP_NAME} — {Path(p).name}");self.statusBar().showMessage(f"{Path(p).name} • {self.image_data.get_dimensions()[0]}×{self.image_data.get_dimensions()[1]}")
        except Exception as e:self.logger.exception("Open failed");QMessageBox.critical(self,"Open failed",str(e))

    def _apply_pipeline(self,image):
        out=image.copy();out=adjust_exposure(out,self.adjustments["exposure"]);out=adjust_brightness(out,self.adjustments["brightness"]);out=adjust_contrast(out,self.adjustments["contrast"]);out=adjust_highlights_shadows(out,self.adjustments["highlights"],self.adjustments["shadows"]);out=adjust_saturation(out,self.adjustments["saturation"]);out=adjust_temperature(out,self.adjustments["temperature"])
        if self.adjustments["tint"]:out=np.clip(out+np.asarray([self.adjustments["tint"]*.12,0,-self.adjustments["tint"]*.12],np.float32),0,1)
        if self.adjustments["vibrance"]:out=apply_vibrance(out,self.adjustments["vibrance"])
        w=self.pro_controls["whites"];b=self.pro_controls["blacks"]
        if w:out=np.clip(out+w*np.power(np.clip(out,0,1),2)*.45,0,1)
        if b:out=np.clip(out+b*(1-np.power(np.clip(out,0,1),2))*.35,0,1)
        if self.pro_controls["clarity"]:out=clarity(out,self.pro_controls["clarity"],4)
        if self.pro_controls["texture"]:out=clarity(out,self.pro_controls["texture"]*.65,1.5)
        if self.pro_controls["dehaze"]:out=adjust_contrast(out,self.pro_controls["dehaze"]*.55)
        if self.active_look and self.look_intensity:
            r=self.active_look.recipe;t=self.look_intensity
            if r.get("exposure"):out=adjust_exposure(out,r["exposure"]*t)
            if r.get("brightness"):out=adjust_brightness(out,r["brightness"]*t)
            if r.get("contrast"):out=adjust_contrast(out,r["contrast"]*t)
            if r.get("highlights") or r.get("shadows"):out=adjust_highlights_shadows(out,r.get("highlights",0)*t,r.get("shadows",0)*t)
            if r.get("saturation"):out=adjust_saturation(out,r["saturation"]*t)
            if r.get("temperature"):out=adjust_temperature(out,r["temperature"]*t)
            if r.get("tint"):out=np.clip(out+np.asarray([r["tint"]*.12*t,0,-r["tint"]*.12*t],np.float32),0,1)
            if r.get("vibrance"):out=apply_vibrance(out,r["vibrance"]*t)
        if self.pro_controls["vignette"]:
            h,w=out.shape[:2];yy,xx=np.ogrid[:h,:w];dx=(xx-w/2)/(w/2);dy=(yy-h/2)/(h/2);v=np.clip(1-(dx*dx+dy*dy)*.55,0,1);amount=self.pro_controls["vignette"];out=np.clip(out*(1+amount*(v[...,None]-1)),0,1)
        if self.pro_controls["grain"]:out=add_grain(out,self.pro_controls["grain"])
        a=self.advanced
        if a["curves_master"] or a["curves_r"] or a["curves_g"] or a["curves_b"]:out=apply_curves(out,a["curves_master"],a["curves_r"],a["curves_g"],a["curves_b"])
        if a["hsl"]:out=apply_hsl(out,**a["hsl"])
        if a["balance"]:out=color_balance(out,**a["balance"])
        if a["selective"]:out=selective_color(out,a["selective"])
        if a["split"]:out=split_tone(out,**a["split"])
        if a["lut"] and Path(a["lut"]).exists():out=apply_cube_lut(out,a["lut"])
        return np.clip(out,0,1).astype(np.float32)

    def render(self):
        if not self.layers:return
        base=self._apply_pipeline(self.image_data.original_image.copy());self.layers.layers[0].pixels=base
        out=self.layers.composite();self.canvas.set_image(out,self.image_data.original_image)
        mean=float(np.mean(out));clip=float(np.mean((out<=.001)|(out>=.999))*100);self.histogram_label.setText(f"Histogram • mean {mean:.3f} • clipped {clip:.1f}% • {out.shape[1]}×{out.shape[0]}")

    def refresh_layers(self):
        if not self.layers:return
        self.layer_list.blockSignals(True);self.layer_list.clear()
        for i,l in enumerate(reversed(self.layers.layers)):
            item=QListWidgetItem(("● " if l.visible else "○ ")+l.name);item.setData(Qt.UserRole,len(self.layers.layers)-1-i);self.layer_list.addItem(item)
        self.layer_list.setCurrentRow(len(self.layers.layers)-1-self.layers.active_index);self.layer_list.blockSignals(False);self.sync_layer_controls()

    def sync_layer_controls(self):
        if not self.layers:return
        l=self.layers.active;self.layer_opacity.blockSignals(True);self.layer_opacity.setValue(round(l.opacity*100));self.layer_opacity.blockSignals(False);self.blend.blockSignals(True);self.blend.setCurrentText(l.blend_mode.value);self.blend.blockSignals(False)

    def select_layer(self,row):
        if self.layers and row>=0:self.layers.active_index=self.layer_list.item(row).data(Qt.UserRole);self.sync_layer_controls()

    def add_layer(self):
        if self.layers:self.layers.add("Retouch Layer");self.refresh_layers();self.render()
    def duplicate_layer(self):
        if self.layers:self.layers.duplicate_active();self.refresh_layers();self.render()
    def delete_layer(self):
        if self.layers:self.layers.delete_active();self.refresh_layers();self.render()
    def move_layer(self,d):
        if self.layers:self.layers.move_active(d);self.refresh_layers();self.render()
    def add_mask(self):
        if self.layers and self.layers.active.mask is None:
            h,w=self.layers.active.pixels.shape[:2];self.layers.active.mask=Mask(w,h,1.);self.render()
    def invert_mask(self):
        if self.layers and self.layers.active.mask:self.layers.active.mask.invert();self.render()
    def set_blend(self,text):
        if self.layers:self.layers.active.blend_mode=BlendMode(text);self.render()
    def set_layer_opacity(self,v):
        if self.layers:self.layers.active.opacity=v/100.;self.render()
    def set_adjustment(self,name,value):
        self.adjustments[name]=float(value);self.render()

    def canvas_to_image(self,x,y):
        if not self.layers:return None
        h,w=self.layers.active.pixels.shape[:2];z=self.canvas.zoom;px=(x-(self.canvas.width()-w*z)/2-self.canvas.pan[0])/z;py=(y-(self.canvas.height()-h*z)/2-self.canvas.pan[1])/z
        return (int(px),int(py)) if 0<=px<w and 0<=py<h else None
    def _snapshot(self):return copy.deepcopy(self.layers.layers),self.layers.active_index,copy.deepcopy(self.adjustments),copy.deepcopy(self.advanced)
    def _restore(self,state):
        self.layers.layers=copy.deepcopy(state[0]);self.layers.active_index=state[1];self.adjustments=copy.deepcopy(state[2]);self.advanced=copy.deepcopy(state[3]);self.refresh_layers();self.render()
    def _commit_state(self,before,name):
        after=self._snapshot();self.undo.execute_command(CallableCommand(name,lambda s=after:self._restore(s),lambda s=before:self._restore(s)))
    def _ensure_retouch_layer(self,name):
        if self.layers.active_index==0:self.layers.add(name)
        l=self.layers.active
        if l.mask is None:l.mask=Mask(l.pixels.shape[1],l.pixels.shape[0],0.)
        return l

    def stroke(self,x,y):
        if not self.layers:return
        pt=self.canvas_to_image(x,y)
        if pt is None:return
        if self.tool=="Clone" and (QApplication.keyboardModifiers() & Qt.AltModifier):
            self.clone_source=pt;self.info.setText("Clone source selected. Release Alt and paint.");return
        before=self._snapshot()
        if self.tool in ("Healing","Clone","Dodge","Burn"):l=self._ensure_retouch_layer(self.tool+" Layer")
        else:l=self.layers.active
        if l.locked:return
        if self.tool=="Mask Paint":
            if l.mask is None:l.mask=Mask(l.pixels.shape[1],l.pixels.shape[0],1.)
            l.mask.paint(pt[0],pt[1],self.brush_size,self.brush_opacity)
        elif self.tool=="Eraser":
            if l.mask is None:l.mask=Mask(l.pixels.shape[1],l.pixels.shape[0],1.)
            l.mask.paint(pt[0],pt[1],self.brush_size,self.brush_opacity,erase=True)
        elif self.tool=="Brush":
            if l.mask is None:l.mask=Mask(l.pixels.shape[1],l.pixels.shape[0],0.)
            base=l.pixels.copy();yy,xx=np.ogrid[:base.shape[0],:base.shape[1]];d=np.sqrt((xx-pt[0])**2+(yy-pt[1])**2);a=np.clip(1-d/max(self.brush_size,1),0,1)**2*self.brush_opacity;color=np.mean(self.layers.composite(),axis=(0,1));l.pixels=base*(1-a[...,None])+color*a[...,None];l.mask.paint(pt[0],pt[1],self.brush_size,self.brush_opacity)
        elif self.tool=="Healing":
            l.pixels=heal_spot(self.layers.composite(),pt,self.brush_size,self.brush_opacity);l.mask.paint(pt[0],pt[1],self.brush_size,self.brush_opacity)
        elif self.tool=="Clone":
            if self.clone_source is None:self.clone_source=pt;self.info.setText("Clone source set. Alt+click another point to change it.");return
            l.pixels=clone_stamp(self.layers.composite(),self.clone_source,pt,self.brush_size,self.brush_opacity);l.mask.paint(pt[0],pt[1],self.brush_size,self.brush_opacity)
        elif self.tool in ("Dodge","Burn"):
            l.pixels=dodge_burn(self.layers.composite(),pt,self.brush_size,.2*self.brush_opacity,"dodge" if self.tool=="Dodge" else "burn");l.mask.paint(pt[0],pt[1],self.brush_size,self.brush_opacity)
        self._commit_state(before,self.tool);self.render()

    def do_undo(self):
        if self.undo.undo():self.render()
    def do_redo(self):
        if self.undo.redo():self.render()

    def reset(self):
        if not self.image_data:return
        self.adjustments={k:0. for k in self.adjustments};self.advanced={"curves_master":None,"curves_r":None,"curves_g":None,"curves_b":None,"hsl":{},"balance":None,"selective":None,"split":None,"lut":None}
        for s in self.adjust_sliders.values():
            if isValid(s):
                s.blockSignals(True);s.setValue(500);s.blockSignals(False)
        self.layers=LayerStack(self.image_data.original_image);self.undo.clear();self.refresh_layers();self.render()

    def add_processed_layer(self,name,data,mask_data=None,blend=BlendMode.NORMAL):
        if not self.layers:return
        l=self.layers.add(name,data);l.blend_mode=blend;l.mask=Mask(data.shape[1],data.shape[0],1.) if mask_data is None else Mask(data.shape[1],data.shape[0],0.)
        if mask_data is not None:l.mask.data=np.clip(mask_data,0,1).astype(np.float32)
        self.refresh_layers();self.render()

    def frequency_separation_action(self):
        if not self.layers:return
        radius,ok=QInputDialog.getDouble(self,"Frequency Separation","Low-frequency radius (px)",8,1,40,1)
        if not ok:return
        image=self.layers.composite();low,high=frequency_separation(image,radius)
        self.layers.add("FS — Low Frequency",low);self.layers.active.mask=Mask(low.shape[1],low.shape[0],1.)
        self.layers.add("FS — High Frequency",high);self.layers.active.blend_mode=BlendMode.LINEAR_LIGHT;self.layers.active.mask=Mask(high.shape[1],high.shape[0],1.)
        self.refresh_layers();self.render();self.info.setText("Frequency Separation created: Low Frequency for tone/color, High Frequency for texture.")
    def skin_smoothing_action(self):
        if not self.layers:return
        strength,ok=QInputDialog.getDouble(self,"Skin Smoothing","Strength",0.25,0,1,2)
        if not ok:return
        radius,ok=QInputDialog.getDouble(self,"Skin Smoothing","Texture radius",4,1,20,1)
        if not ok:return
        image=self.layers.composite();mask=make_skin_mask(image);sm=skin_smooth(image,mask,radius,strength);self.add_processed_layer("Skin — Natural Smoothing",sm,mask);self.info.setText("Manual classical skin mask + edge-preserving smoothing. No AI.")
    def skin_tone_action(self):
        if not self.layers:return
        strength,ok=QInputDialog.getDouble(self,"Skin Tone Balance","Strength",0.25,0,1,2)
        if not ok:return
        image=self.layers.composite();mask=make_skin_mask(image);out=skin_tone_correct(image,strength=strength,mask=mask);self.add_processed_layer("Skin — Tone Balance",out,mask);self.info.setText("Skin tone balancing is mask-based and deterministic.")
    def detail_action(self,kind):
        if not self.layers:return
        image=self.layers.composite()
        if kind=="sharpen":
            amount,ok=QInputDialog.getDouble(self,"Sharpen","Amount",0.7,0,3,2)
            if not ok:return
            data=sharpen(image,amount,1.0,.03);name="Detail — Sharpen"
        elif kind=="clarity":
            amount,ok=QInputDialog.getDouble(self,"Clarity","Amount",0.25,-1,1,2)
            if not ok:return
            data=clarity(image,amount,4);name="Detail — Clarity"
        elif kind=="denoise":
            amount,ok=QInputDialog.getDouble(self,"Denoise","Strength",0.25,0,1,2)
            if not ok:return
            data=denoise(image,amount);name="Detail — Noise Reduction"
        else:
            amount,ok=QInputDialog.getDouble(self,"Film Grain","Amount",0.03,0,0.2,3)
            if not ok:return
            data=add_grain(image,amount);name="Look — Film Grain"
        self.add_processed_layer(name,data);self.info.setText(f"{name} applied as a separate editable layer.")

    def curves_dialog(self):
        if not self.layers:return
        text,ok=QInputDialog.getText(self,"RGB Curves","Master points x:y (comma separated)",text="0:0,0.25:0.2,0.5:0.5,0.75:0.8,1:1")
        if not ok:return
        try:
            pts=[tuple(map(float,p.strip().split(":"))) for p in text.split(",")];self.advanced["curves_master"]=pts;self.render()
        except Exception as e:QMessageBox.warning(self,"Curves",f"Invalid points: {e}")
    def hsl_dialog(self):
        h,ok=QInputDialog.getDouble(self,"HSL","Hue shift (-1..1)",0,-1,1,3)
        if not ok:return
        s,ok=QInputDialog.getDouble(self,"HSL","Saturation (-1..1)",0,-1,1,3)
        if not ok:return
        l,ok=QInputDialog.getDouble(self,"HSL","Luminance (-1..1)",0,-1,1,3)
        if ok:self.advanced["hsl"]={"hue":h,"saturation":s,"luminance":l};self.render()
    def color_balance_dialog(self):
        sh,ok=QInputDialog.getText(self,"Color Balance","Shadows RGB offsets, e.g. -0.02,0,0.03",text="0,0,0")
        if not ok:return
        mi,ok=QInputDialog.getText(self,"Color Balance","Midtones RGB offsets",text="0,0,0")
        if not ok:return
        hi,ok=QInputDialog.getText(self,"Color Balance","Highlights RGB offsets",text="0,0,0")
        if not ok:return
        try:
            parse=lambda x:tuple(float(v.strip()) for v in x.split(","))
            self.advanced["balance"]={"shadows":parse(sh),"midtones":parse(mi),"highlights":parse(hi),"strength":1.0};self.render()
        except Exception as e:QMessageBox.warning(self,"Color Balance",str(e))
    def selective_color_dialog(self):
        name,ok=QInputDialog.getItem(self,"Selective Color","Color family",["reds","yellows","greens","cyans","blues","magentas","neutrals"],0,False)
        if not ok:return
        values,ok=QInputDialog.getText(self,"Selective Color","RGB offsets -100..100",text="0,0,0")
        if ok:
            try:self.advanced["selective"]={name:tuple(float(v.strip()) for v in values.split(","))};self.render()
            except Exception as e:QMessageBox.warning(self,"Selective Color",str(e))
    def split_tone_dialog(self):
        amount,ok=QInputDialog.getDouble(self,"Split Toning","Amount",0.12,0,1,2)
        if not ok:return
        self.advanced["split"]={"amount":amount,"shadow_rgb":(0.08,0.10,0.16),"highlight_rgb":(0.95,0.82,0.65),"balance":0.0};self.render()
    def load_lut(self):
        p,_=QFileDialog.getOpenFileName(self,"Load .cube LUT","", "3D LUT (*.cube)")
        if p:
            try:self.advanced["lut"]=p;self.render();self.info.setText(f"LUT loaded: {Path(p).name}")
            except Exception as e:QMessageBox.critical(self,"LUT failed",str(e))
    def quick_vibrance(self,value):self.adjustments["vibrance"]=value;self.render()

    def _preset_state(self):
        return {"adjustments":self.adjustments.copy(),"color":self.advanced.copy()}
    def apply_preset_dialog(self):
        names=self.preset_manager.list_names();name,ok=QInputDialog.getItem(self,"Apply Preset","Preset",names,0,False)
        if not ok:return
        data=self.preset_manager.get(name);data=data.get("settings",data);self.adjustments.update(data.get("adjustments",{}))
        color=data.get("color",{}); 
        if "shadows" in color or "highlights" in color:self.advanced["balance"]={"shadows":tuple(color.get("shadows",(0,0,0))),"midtones":tuple(color.get("midtones",(0,0,0))),"highlights":tuple(color.get("highlights",(0,0,0))),"strength":1.0}
        if "amount" in color:self.advanced["split"]=color
        for k,v in self.adjustments.items():
            if k in self.adjust_sliders:
                lo,hi={"exposure":(-2,2),"brightness":(-1,1),"contrast":(-1,1),"highlights":(-1,1),"shadows":(-1,1),"saturation":(-1,1),"temperature":(-1,1),"tint":(-1,1),"vibrance":(-1,1)}[k]
                self.adjust_sliders[k].blockSignals(True);self.adjust_sliders[k].setValue(round((v-lo)/(hi-lo)*1000));self.adjust_sliders[k].blockSignals(False)
        self.render();self.info.setText(f"Preset applied: {name}")
    def save_preset(self):
        if not self.layers:return
        name,ok=QInputDialog.getText(self,"Save Preset","Preset name")
        if ok and name.strip():
            try:self.preset_manager.save(name,self._preset_state());self.info.setText(f"Preset saved: {name}")
            except Exception as e:QMessageBox.warning(self,"Preset",str(e))
    def open_preset_folder(self):
        import os
        p=str(self.preset_manager.directory);os.startfile(p) if sys.platform=="win32" else None

    def save_project(self):
        if not self.layers or not self.image_data:return
        p,_=QFileDialog.getSaveFileName(self,"Save Project","", "ALIS DEJA VU Project (*.alis)")
        if not p:return
        try:
            temp=copy.deepcopy(self.layers);temp.layers[0].pixels=self.image_data.original_image.copy()
            ProjectFile.save(p,self.image_data.file_path,self.adjustments,temp,{"app_version":APP_VERSION,"advanced":self.advanced})
            self.statusBar().showMessage(f"Project saved: {Path(p).name}")
        except Exception as e:self.logger.exception("Project save failed");QMessageBox.critical(self,"Save Project failed",str(e))

    def open_project(self):
        p,_=QFileDialog.getOpenFileName(self,"Open Project","", "ALIS DEJA VU Project (*.alis)")
        if not p:return
        try:
            import json,zipfile
            with zipfile.ZipFile(p) as z:manifest=json.loads(z.read("manifest.json").decode("utf-8"))
            original=Path(manifest["original_path"])
            if not original.exists():
                QMessageBox.warning(self,"Original image missing",f"The project references:
{original}

Move the original image back to this path before opening the project.")
                return
            self.image_data=ImageData(str(original));_,self.layers=ProjectFile.load(p,LayerStack,Mask,BlendMode);self.adjustments.update(manifest.get("adjustments",{}));self.advanced.update(manifest.get("metadata",{}).get("advanced",{}));self.undo.clear();self.refresh_layers();self.render();self.canvas.fit_to_window();self.setWindowTitle(f"{APP_NAME} — {Path(p).name}")
        except Exception as e:self.logger.exception("Project open failed");QMessageBox.critical(self,"Open Project failed",str(e))

    def export(self):
        if not self.layers:return
        p,_=QFileDialog.getSaveFileName(self,"Export Image","",EXPORT_FORMATS_FILTER)
        if not p:return
        quality,ok=QInputDialog.getInt(self,"Export","JPEG quality (used for JPEG)",self.settings.get("default_jpeg_quality",95),1,100)
        if not ok:return
        try:export_image(self.layers.composite(),p,quality=quality);self.statusBar().showMessage(f"Exported: {Path(p).name}")
        except Exception as e:self.logger.exception("Export failed");QMessageBox.critical(self,"Export failed",str(e))

    def settings_dialog(self):
        d=QDialog(self);d.setWindowTitle("ALIS DEJA VU Settings");form=QFormLayout(d)
        threads=QSpinBox();threads.setRange(1,32);threads.setValue(int(self.settings.get("worker_threads",2)));cache=QSpinBox();cache.setRange(1,32);cache.setValue(int(self.settings.get("cache_items",8)));quality=QSpinBox();quality.setRange(1,100);quality.setValue(int(self.settings.get("default_jpeg_quality",95)));auto=QCheckBox();auto.setChecked(bool(self.settings.get("autosave",True)))
        form.addRow("Worker threads",threads);form.addRow("Preview cache items",cache);form.addRow("Default JPEG quality",quality);form.addRow("Autosave preference",auto)
        box=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);box.accepted.connect(d.accept);box.rejected.connect(d.reject);form.addRow(box)
        if d.exec():
            self.settings.set("worker_threads",threads.value());self.settings.set("cache_items",cache.value());self.settings.set("default_jpeg_quality",quality.value());self.settings.set("autosave",auto.isChecked());self.settings.save();self.cache=PreviewCache(cache.value());self.thread_pool.setMaxThreadCount(threads.value())
    def clear_cache(self):self.cache.clear();self.info.setText("Preview cache cleared.")

if __name__=="__main__":
    from PySide6.QtWidgets import QApplication
    app=QApplication(sys.argv);app.setApplicationName(APP_NAME);app.setApplicationVersion(APP_VERSION);app.setStyle("Fusion");w=MainWindow();w.show();sys.exit(app.exec())
