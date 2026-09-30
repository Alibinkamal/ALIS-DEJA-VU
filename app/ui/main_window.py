import sys,copy
import numpy as np
from pathlib import Path
from PySide6.QtWidgets import QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QFileDialog,QMessageBox,QListWidget,QListWidgetItem,QPushButton,QLabel,QComboBox,QSlider,QApplication
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt
from app import APP_NAME,APP_VERSION
from app.core import ImageData,LayerStack,UndoRedoManager,CallableCommand
from app.core.layers import BlendMode
from app.core.masks import Mask
from app.image import ImageSaver,SUPPORTED_FORMATS_FILTER,EXPORT_FORMATS_FILTER
from app.processing import heal_spot,clone_stamp,dodge_burn,adjust_exposure,adjust_brightness,adjust_contrast,adjust_saturation,adjust_temperature
from app.ui.widgets import ImageCanvas
from app.ui.theme import StyleSheet
class MainWindow(QMainWindow):
 def __init__(self):
  super().__init__();self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}");self.resize(1450,900);self.image_data=None;self.layers=None;self.undo=UndoRedoManager(40);self.tool="Brush";self.brush_size=40;self.brush_opacity=1.;self.clone_source=None;self.adjustments={"exposure":0.,"brightness":0.,"contrast":0.,"saturation":0.,"temperature":0.};self._build();self._menus()
 def _build(self):
  root=QWidget();self.setCentralWidget(root);main=QHBoxLayout(root);main.setContentsMargins(0,0,0,0)
  left=QWidget();left.setFixedWidth(210);self.tools=QVBoxLayout(left);main.addWidget(left)
  for name in ["Brush","Mask Paint","Eraser","Healing","Clone","Dodge","Burn"]:
   b=QPushButton(name);b.clicked.connect(lambda _,n=name:self.set_tool(n));self.tools.addWidget(b)
  self.tools.addWidget(QLabel("Brush Size"));self.size=QSlider(Qt.Horizontal);self.size.setRange(2,400);self.size.setValue(40);self.size.valueChanged.connect(lambda v:setattr(self,"brush_size",v));self.tools.addWidget(self.size)
  self.tools.addWidget(QLabel("Opacity"));self.opacity=QSlider(Qt.Horizontal);self.opacity.setRange(1,100);self.opacity.setValue(100);self.opacity.valueChanged.connect(lambda v:setattr(self,"brush_opacity",v/100));self.tools.addWidget(self.opacity)
  self.invert_btn=QPushButton("Invert Active Mask");self.invert_btn.clicked.connect(self.invert_mask);self.tools.addWidget(self.invert_btn);self.tools.addStretch()
  self.canvas=ImageCanvas();self.canvas.stroke.connect(self.stroke);main.addWidget(self.canvas,1)
  right=QWidget();right.setFixedWidth(280);self.panel=QVBoxLayout(right);main.addWidget(right)
  self.panel.addWidget(QLabel("LAYERS"));self.layer_list=QListWidget();self.layer_list.currentRowChanged.connect(self.select_layer);self.panel.addWidget(self.layer_list,1)
  for text,fn in [("＋ Layer",self.add_layer),("Duplicate",self.duplicate_layer),("Delete",self.delete_layer),("↑ Move Up",lambda:self.move_layer(-1)),("↓ Move Down",lambda:self.move_layer(1)),("Add Mask",self.add_mask)]:
   b=QPushButton(text);b.clicked.connect(fn);self.panel.addWidget(b)
  self.panel.addWidget(QLabel("Blend Mode"));self.blend=QComboBox();self.blend.addItems([x.value for x in BlendMode]);self.blend.currentTextChanged.connect(self.set_blend);self.panel.addWidget(self.blend)
  self.panel.addWidget(QLabel("Layer Opacity"));self.layer_opacity=QSlider(Qt.Horizontal);self.layer_opacity.setRange(0,100);self.layer_opacity.setValue(100);self.layer_opacity.valueChanged.connect(self.set_layer_opacity);self.panel.addWidget(self.layer_opacity);
  self.panel.addWidget(QLabel("BASIC ADJUSTMENTS"))
  self.adjust_sliders={}
  for name,lo,hi in [("exposure",-2,2),("brightness",-1,1),("contrast",-1,1),("saturation",-1,1),("temperature",-1,1)]:
   row=QHBoxLayout();row.addWidget(QLabel(name.title()));s=QSlider(Qt.Horizontal);s.setRange(0,1000);s.setValue(500);s.valueChanged.connect(lambda v,n=name,a=lo,b=hi:self.set_adjustment(n,a+(b-a)*v/1000));row.addWidget(s);self.panel.addLayout(row);self.adjust_sliders[name]=s
  self.histogram_label=QLabel("Histogram: no image");self.histogram_label.setWordWrap(True);self.panel.addWidget(self.histogram_label)
  self.retouch_info=QLabel("Phase 3: layers, masks and brush engine. Phase 4: Healing, Clone, Dodge and Burn.");self.retouch_info.setWordWrap(True);self.panel.addWidget(self.retouch_info)
  self.statusBar().showMessage("Ready — Open an image to begin");self.setStyleSheet(StyleSheet.get_stylesheet())
 def _menus(self):
  m=self.menuBar();f=m.addMenu("File");a=f.addAction("Open Image");a.setShortcut(QKeySequence.Open);a.triggered.connect(self.open_image);a=f.addAction("Export As");a.setShortcut(QKeySequence.SaveAs);a.triggered.connect(self.export);f.addSeparator();f.addAction("Exit",self.close)
  e=m.addMenu("Edit");u=e.addAction("Undo");u.setShortcut(QKeySequence.Undo);u.triggered.connect(self.do_undo);r=e.addAction("Redo");r.setShortcut(QKeySequence.Redo);r.triggered.connect(self.do_redo);e.addSeparator();e.addAction("Reset",self.reset)
  v=m.addMenu("View");v.addAction("Fit",self.canvas.fit_to_window);v.addAction("100%",self.canvas.actual_size);v.addAction("Zoom In",self.canvas.zoom_in);v.addAction("Zoom Out",self.canvas.zoom_out)
 def set_tool(self,t):self.tool=t;self.clone_source=None;self.retouch_info.setText(f"Active tool: {t}. {'Clone uses Alt+click to choose a source.' if t=='Clone' else 'Paint directly on the canvas.'}")
 def open_image(self):
  p,_=QFileDialog.getOpenFileName(self,"Open Image","",SUPPORTED_FORMATS_FILTER)
  if p:self.load_image(p)
 def load_image(self,p):
  try:
   from app.core import ImageData
   self.image_data=ImageData(p);self.adjustments={k:0. for k in self.adjustments};self.layers=LayerStack(self.image_data.original_image);self.undo.clear();self.refresh_layers();self.render();self.canvas.fit_to_window();self.setWindowTitle(f"{APP_NAME} — {Path(p).name}");self.statusBar().showMessage(f"{Path(p).name} • {self.image_data.get_dimensions()[0]}×{self.image_data.get_dimensions()[1]}")
  except Exception as e:QMessageBox.critical(self,"Open failed",str(e))
 def render(self):
  if not self.layers:return
  base=self.image_data.original_image.copy()
  base=adjust_exposure(base,self.adjustments["exposure"]);base=adjust_brightness(base,self.adjustments["brightness"]);base=adjust_contrast(base,self.adjustments["contrast"]);base=adjust_saturation(base,self.adjustments["saturation"]);base=adjust_temperature(base,self.adjustments["temperature"])
  self.layers.layers[0].pixels=base
  out=self.layers.composite();self.canvas.set_image(out,self.image_data.original_image)
  mean=float(np.mean(out));clip=float(np.mean((out<=0.001)|(out>=0.999))*100);self.histogram_label.setText(f"Histogram • mean {mean:.3f} • clipped {clip:.1f}%")
 def refresh_layers(self):
  if not self.layers:return
  self.layer_list.blockSignals(True);self.layer_list.clear()
  for i,l in enumerate(reversed(self.layers.layers)):
   item=QListWidgetItem(("● " if l.visible else "○ ")+l.name);item.setData(Qt.UserRole,len(self.layers.layers)-1-i);self.layer_list.addItem(item)
  self.layer_list.setCurrentRow(len(self.layers.layers)-1-self.layers.active_index);self.layer_list.blockSignals(False);self.sync_layer_controls()
 def sync_layer_controls(self):
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
 def _snapshot(self):return copy.deepcopy(self.layers.layers),self.layers.active_index
 def _restore(self,state):self.layers.layers=copy.deepcopy(state[0]);self.layers.active_index=state[1];self.refresh_layers();self.render()
 def _commit_state(self,before,name):
  after=self._snapshot();self.undo.execute_command(CallableCommand(name,lambda s=after:self._restore(s),lambda s=before:self._restore(s)))
 def _ensure_retouch_layer(self,name):
  if self.layers.active_index==0:self.layers.add(name);self.refresh_layers()
  l=self.layers.active
  if l.mask is None:l.mask=Mask(l.pixels.shape[1],l.pixels.shape[0],0.)
  return l
 def stroke(self,x,y):
  if not self.layers:return
  pt=self.canvas_to_image(x,y)
  if pt is None:return
  if self.tool=="Clone" and (QApplication.keyboardModifiers() & Qt.AltModifier):
   self.clone_source=pt;self.retouch_info.setText("Clone source selected. Release Alt and paint.");return
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
   if self.clone_source is None:self.clone_source=pt;self.retouch_info.setText("Clone source set. Alt+click another point to change it.");return
   l.pixels=clone_stamp(self.layers.composite(),self.clone_source,pt,self.brush_size,self.brush_opacity);l.mask.paint(pt[0],pt[1],self.brush_size,self.brush_opacity)
  elif self.tool in ("Dodge","Burn"):
   l.pixels=dodge_burn(self.layers.composite(),pt,self.brush_size,.2*self.brush_opacity,"dodge" if self.tool=="Dodge" else "burn");l.mask.paint(pt[0],pt[1],self.brush_size,self.brush_opacity)
  self._commit_state(before,self.tool);self.render()
 def do_undo(self):
  if self.undo.undo():self.render()
 def do_redo(self):
  if self.undo.redo():self.render()
 def reset(self):
  if self.image_data:
   self.adjustments={k:0. for k in self.adjustments}
   for s in self.adjust_sliders.values():s.blockSignals(True);s.setValue(500);s.blockSignals(False)
   self.layers=LayerStack(self.image_data.original_image);self.undo.clear();self.refresh_layers();self.render()
 def export(self):
  if not self.layers:return
  p,_=QFileDialog.getSaveFileName(self,"Export Image","",EXPORT_FORMATS_FILTER)
  if p:
   try:ImageSaver.save(self.layers.composite(),p);self.statusBar().showMessage(f"Exported: {Path(p).name}")
   except Exception as e:QMessageBox.critical(self,"Export failed",str(e))
