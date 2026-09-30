import numpy as np
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QSlider,QDoubleSpinBox,QGroupBox
from PySide6.QtGui import QImage,QPixmap,QPainter
from PySide6.QtCore import Qt,Signal
from app.ui.theme import Colors
class ImageCanvas(QWidget):
 zoom_changed=Signal(float); position_changed=Signal(int,int); stroke=Signal(int,int)
 def __init__(self,parent=None):
  super().__init__(parent); self.image_data=None; self.original=None; self.zoom=1.; self.pan=[0,0]; self.drag=None; self.setFocusPolicy(Qt.StrongFocus); self.setStyleSheet(f"background:{Colors.CANVAS_BACKGROUND.name()};")
 def set_image(self,a,original=None): self.image_data=a; self.original=original if original is not None else a; self.update()
 def update_pixmap(self): self.update()
 def paintEvent(self,e):
  p=QPainter(self); p.fillRect(self.rect(),Colors.CANVAS_BACKGROUND)
  if self.image_data is None:return
  a=np.ascontiguousarray(np.clip(self.image_data*255,0,255).astype(np.uint8)); h,w=a.shape[:2]; q=QImage(a.data,w,h,3*w,QImage.Format_RGB888); pm=QPixmap.fromImage(q).scaled(int(w*self.zoom),int(h*self.zoom),Qt.KeepAspectRatio,Qt.SmoothTransformation); x=(self.width()-pm.width())//2+self.pan[0]; y=(self.height()-pm.height())//2+self.pan[1]; p.drawPixmap(x,y,pm)
 def fit_to_window(self):
  if self.image_data is None:return
  h,w=self.image_data.shape[:2]; self.zoom=min(self.width()/w,self.height()/h)*.95; self.pan=[0,0]; self.zoom_changed.emit(self.zoom); self.update()
 def actual_size(self): self.zoom=1.; self.pan=[0,0]; self.zoom_changed.emit(1.); self.update()
 def zoom_in(self): self.zoom=min(self.zoom*1.25,16); self.zoom_changed.emit(self.zoom); self.update()
 def zoom_out(self): self.zoom=max(self.zoom/1.25,.05); self.zoom_changed.emit(self.zoom); self.update()
 def wheelEvent(self,e): self.zoom_in() if e.angleDelta().y()>0 else self.zoom_out()
 def mousePressEvent(self,e):
  if e.button()==Qt.MiddleButton: self.drag=e.position().toPoint(); self.setCursor(Qt.ClosedHandCursor)
  elif e.button()==Qt.LeftButton:self.stroke.emit(int(e.position().x()),int(e.position().y()))
 def mouseMoveEvent(self,e):
  if self.drag is not None: d=e.position().toPoint()-self.drag; self.pan[0]+=d.x(); self.pan[1]+=d.y(); self.drag=e.position().toPoint(); self.update()
  elif e.buttons()&Qt.LeftButton:self.stroke.emit(int(e.position().x()),int(e.position().y()))
 def mouseReleaseEvent(self,e):
  if e.button()==Qt.MiddleButton:self.drag=None; self.setCursor(Qt.OpenHandCursor)
class ControlPanel(QGroupBox):
 def __init__(self,title,parent=None): super().__init__(title,parent); self._layout=QVBoxLayout(self); self._layout.setSpacing(5)
 def add_slider_control(self,label,minimum,maximum,value,callback):
  row=QHBoxLayout(); row.addWidget(QLabel(label)); spin=QDoubleSpinBox(); spin.setRange(minimum,maximum); spin.setValue(value); spin.setSingleStep((maximum-minimum)/100); slider=QSlider(Qt.Horizontal); slider.setRange(0,1000); slider.setValue(int((value-minimum)/(maximum-minimum)*1000));
  def changed(v): x=minimum+(maximum-minimum)*v/1000; spin.blockSignals(True); spin.setValue(x); spin.blockSignals(False); callback(x)
  def spin_changed(x): slider.blockSignals(True); slider.setValue(int((x-minimum)/(maximum-minimum)*1000)); slider.blockSignals(False); callback(x)
  slider.valueChanged.connect(changed); spin.valueChanged.connect(spin_changed); row.addWidget(slider,1); row.addWidget(spin); self._layout.addLayout(row); return slider,spin
