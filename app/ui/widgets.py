import numpy as np
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QSlider,QDoubleSpinBox,QGroupBox
from PySide6.QtGui import QImage,QPixmap,QPainter
from PySide6.QtCore import Qt,Signal,QPoint
from app.ui.theme import Colors

class ImageCanvas(QWidget):
    zoom_changed=Signal(float); position_changed=Signal(int,int); stroke=Signal(int,int); file_dropped=Signal(str)
    def __init__(self,parent=None):
        super().__init__(parent);self.image_data=None;self.original=None;self.zoom=1.;self.pan=[0,0];self.drag=None;self.show_original=False
        self.setFocusPolicy(Qt.StrongFocus);self.setAcceptDrops(True);self.setStyleSheet(f"background:{Colors.CANVAS_BACKGROUND.name()};")
    def set_image(self,a,original=None):
        self.image_data=a;self.original=original if original is not None else a;self.update()
    def set_before_after(self,before=False):
        self.show_original=bool(before);self.update()
    def paintEvent(self,e):
        p=QPainter(self);p.fillRect(self.rect(),Colors.CANVAS_BACKGROUND)
        a0=self.original if self.show_original else self.image_data
        if a0 is None:return
        a=np.ascontiguousarray(np.clip(a0*255,0,255).astype(np.uint8));h,w=a.shape[:2]
        q=QImage(a.data,w,h,3*w,QImage.Format_RGB888);pm=QPixmap.fromImage(q).scaled(int(w*self.zoom),int(h*self.zoom),Qt.KeepAspectRatio,Qt.SmoothTransformation)
        x=(self.width()-pm.width())//2+self.pan[0];y=(self.height()-pm.height())//2+self.pan[1];p.drawPixmap(x,y,pm)
        if self.show_original:
            p.setPen(Colors.ACCENT_PRIMARY);p.drawText(16,24,"BEFORE — Original")
    def fit_to_window(self):
        a=self.image_data
        if a is None:return
        h,w=a.shape[:2];self.zoom=max(.05,min(self.width()/w,self.height()/h)*.95);self.pan=[0,0];self.zoom_changed.emit(self.zoom);self.update()
    def actual_size(self):self.zoom=1.;self.pan=[0,0];self.zoom_changed.emit(1.);self.update()
    def zoom_in(self):self.zoom=min(self.zoom*1.25,16);self.zoom_changed.emit(self.zoom);self.update()
    def zoom_out(self):self.zoom=max(self.zoom/1.25,.05);self.zoom_changed.emit(self.zoom);self.update()
    def wheelEvent(self,e):self.zoom_in() if e.angleDelta().y()>0 else self.zoom_out()
    def mousePressEvent(self,e):
        if e.button()==Qt.MiddleButton:self.drag=e.position().toPoint();self.setCursor(Qt.ClosedHandCursor)
        elif e.button()==Qt.LeftButton and not self.show_original:self.stroke.emit(int(e.position().x()),int(e.position().y()))
    def mouseMoveEvent(self,e):
        if self.drag is not None:
            d=e.position().toPoint()-self.drag;self.pan[0]+=d.x();self.pan[1]+=d.y();self.drag=e.position().toPoint();self.update()
        elif e.buttons()&Qt.LeftButton and not self.show_original:self.stroke.emit(int(e.position().x()),int(e.position().y()))
    def mouseReleaseEvent(self,e):
        if e.button()==Qt.MiddleButton:self.drag=None;self.setCursor(Qt.OpenHandCursor)
    def dragEnterEvent(self,e):
        if e.mimeData().hasUrls() and any(u.isLocalFile() for u in e.mimeData().urls()):e.acceptProposedAction()
    def dropEvent(self,e):
        for u in e.mimeData().urls():
            if u.isLocalFile():self.file_dropped.emit(u.toLocalFile());break
        e.acceptProposedAction()

class ControlPanel(QGroupBox):
    def __init__(self,title,parent=None):
        super().__init__(title,parent);self._layout=QVBoxLayout(self);self._layout.setSpacing(5)
    def add_slider_control(self,label,minimum,maximum,value,callback):
        row=QHBoxLayout();row.addWidget(QLabel(label));spin=QDoubleSpinBox();spin.setRange(minimum,maximum);spin.setValue(value);spin.setSingleStep((maximum-minimum)/100);slider=QSlider(Qt.Horizontal);slider.setRange(0,1000);slider.setValue(int((value-minimum)/(maximum-minimum)*1000))
        def changed(v):
            x=minimum+(maximum-minimum)*v/1000;spin.blockSignals(True);spin.setValue(x);spin.blockSignals(False);callback(x)
        def spin_changed(x):
            slider.blockSignals(True);slider.setValue(int((x-minimum)/(maximum-minimum)*1000));slider.blockSignals(False);callback(x)
        slider.valueChanged.connect(changed);spin.valueChanged.connect(spin_changed);row.addWidget(slider,1);row.addWidget(spin);self._layout.addLayout(row);return slider,spin
