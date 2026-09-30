from pathlib import Path
import copy
import numpy as np
from PySide6.QtWidgets import QDialog,QFormLayout,QDialogButtonBox,QDoubleSpinBox,QSpinBox,QCheckBox,QComboBox,QInputDialog,QMessageBox,QFileDialog,QPushButton,QVBoxLayout,QLabel
from PySide6.QtCore import Qt,QRectF
from PySide6.QtGui import QImage,QPainter,QFont,QColor
from app.ui.main_window import MainWindow
from app import APP_NAME,APP_VERSION
from app.core.layers import LayerStack
from app.core.layers import BlendMode
from app.core.masks import Mask
from app.ui.widgets import TextOverlay
from app.export import export_image\nfrom app.project import ProjectFile\nfrom app.image import ImageData\nfrom app.utils import get_logger
from app.processing.pro_tools import color_wheels,apply_vignette,bloom,halation,tone_curve,linear_gradient_mask,radial_mask,crop_array,transform_array

class ProMainWindow(MainWindow):
    """Phase 9-17 professional extension layer.

    Keeps the original MainWindow architecture intact while adding masks,
    advanced color, geometry, typography studio, export studio, and release
    hardening controls in a separate orchestration layer.
    """
    def __init__(self):
        self.pro_grade={"shadows":(0.,0.,0.),"midtones":(0.,0.,0.),"highlights":(0.,0.,0.),"balance":0.,"strength":1.}
        self.pro_effects={"bloom":0.,"halation":0.}
        self.preview_max_side=1800
        self._studio_menu=None
        super().__init__()

    def _menus(self):
        super()._menus()
        m=self.menuBar()
        studio=m.addMenu("PRO STUDIO")
        studio.addAction("Masking Studio",self.masking_dialog)
        studio.addAction("Color Wheels",self.color_wheels_dialog)
        studio.addAction("Crop / Geometry",self.geometry_dialog)
        studio.addAction("Typography Studio",self.typography_studio)
        studio.addAction("Export Studio",self.export_studio)
        studio.addAction("Performance / Preview",self.performance_dialog)
        studio.addSeparator()
        studio.addAction("Reset Pro Controls",self.reset_pro_controls)
        self._studio_menu=studio

    def _snapshot(self):
        base=super()._snapshot()
        return base+(copy.deepcopy(self.pro_grade),copy.deepcopy(self.pro_effects),copy.deepcopy(self.text_overlays))

    def _restore(self,state):
        super()._restore(state[:4])
        if len(state)>4:self.pro_grade=copy.deepcopy(state[4])
        if len(state)>5:self.pro_effects=copy.deepcopy(state[5])
        if len(state)>6:self.text_overlays=copy.deepcopy(state[6]);self.canvas.text_overlays=self.text_overlays
        self.render()

    def _apply_pipeline(self,image):
        out=super()._apply_pipeline(image)
        g=self.pro_grade
        if any(abs(x)>1e-6 for group in (g["shadows"],g["midtones"],g["highlights"]) for x in group) or abs(g["balance"])>1e-6:
            out=color_wheels(out,g["shadows"],g["midtones"],g["highlights"],g["balance"],g["strength"])
        if self.pro_effects["bloom"]:out=bloom(out,self.pro_effects["bloom"],8+18*self.pro_effects["bloom"])
        if self.pro_effects["halation"]:out=halation(out,self.pro_effects["halation"],4+10*self.pro_effects["halation"])
        return out

    def reset_pro_controls(self):
        self.pro_grade={"shadows":(0.,0.,0.),"midtones":(0.,0.,0.),"highlights":(0.,0.,0.),"balance":0.,"strength":1.}
        self.pro_effects={"bloom":0.,"halation":0.}
        self.render()

    def _mask_from_dialog(self,kind):
        if not self.layers:return
        h,w=self.layers.active.pixels.shape[:2]
        if kind=="gradient":
            angle,ok=QInputDialog.getDouble(self,"Linear Gradient Mask","Angle",90,-360,360,1)
            if not ok:return
            softness,ok=QInputDialog.getDouble(self,"Linear Gradient Mask","Feather",0.20,0.01,1,2)
            if not ok:return
            data=linear_gradient_mask(h,w,angle,softness)
        else:
            cx,ok=QInputDialog.getDouble(self,"Radial Mask","Center X (0..1)",.5,0,1,2)
            if not ok:return
            cy,ok=QInputDialog.getDouble(self,"Radial Mask","Center Y (0..1)",.5,0,1,2)
            if not ok:return
            radius,ok=QInputDialog.getDouble(self,"Radial Mask","Radius",.5,.02,1.5,2)
            if not ok:return
            feather,ok=QInputDialog.getDouble(self,"Radial Mask","Feather",.25,.01,1,2)
            if not ok:return
            data=radial_mask(h,w,cx,cy,radius,feather)
        self.layers.active.mask=Mask(w,h,0);self.layers.active.mask.data=data;self.render();self.info.setText(f"{kind.title()} mask created.")

    def masking_dialog(self):
        if not self.layers:return
        d=QDialog(self);d.setWindowTitle("Masking Studio");lay=QVBoxLayout(d)
        lay.addWidget(QLabel("Non-destructive masks — paint, gradient and radial controls"))
        for title,kind in [("Linear Gradient","gradient"),("Radial Mask","radial")]:
            b=QPushButton(title);b.clicked.connect(lambda _,k=kind:self._mask_from_dialog(k));lay.addWidget(b)
        inv=QPushButton("Invert Active Mask");inv.clicked.connect(self.invert_mask);lay.addWidget(inv)
        box=QDialogButtonBox(QDialogButtonBox.Close);box.rejected.connect(d.reject);lay.addWidget(box);d.exec()

    def color_wheels_dialog(self):
        if not self.layers:return
        d=QDialog(self);d.setWindowTitle("Color Grading — 3 Way Wheels");form=QFormLayout(d)
        spins={}
        for group in ("shadows","midtones","highlights"):
            for ch in ("R","G","B"):
                s=QDoubleSpinBox();s.setRange(-.5,.5);s.setSingleStep(.01);s.setValue(float(self.pro_grade[group][("R","G","B").index(ch)]));form.addRow(f"{group.title()} {ch}",s);spins[(group,ch)]=s
        bal=QDoubleSpinBox();bal.setRange(-1,1);bal.setSingleStep(.05);bal.setValue(self.pro_grade["balance"]);form.addRow("Balance",bal)
        strength=QDoubleSpinBox();strength.setRange(0,2);strength.setSingleStep(.05);strength.setValue(self.pro_grade["strength"]);form.addRow("Strength",strength)
        bloom_s=QDoubleSpinBox();bloom_s.setRange(0,1);bloom_s.setSingleStep(.05);bloom_s.setValue(self.pro_effects["bloom"]);form.addRow("Bloom",bloom_s)
        halo_s=QDoubleSpinBox();halo_s.setRange(0,1);halo_s.setSingleStep(.05);halo_s.setValue(self.pro_effects["halation"]);form.addRow("Halation",halo_s)
        box=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);box.accepted.connect(d.accept);box.rejected.connect(d.reject);form.addRow(box)
        if d.exec():
            for group in ("shadows","midtones","highlights"):self.pro_grade[group]=tuple(spins[(group,ch)].value() for ch in ("R","G","B"))
            self.pro_grade["balance"]=bal.value();self.pro_grade["strength"]=strength.value();self.pro_effects["bloom"]=bloom_s.value();self.pro_effects["halation"]=halo_s.value();self.render();self.info.setText("3-way color grading updated.")

    def _transform_all_layers(self,fn):
        if not self.layers:return
        for layer in self.layers.layers:
            layer.pixels=fn(layer.pixels)
            if layer.mask is not None:
                m=fn(layer.mask.data[...,None].repeat(3,axis=2))[:,:,0];layer.mask=Mask(m.shape[1],m.shape[0],0);layer.mask.data=m.astype(np.float32)
        self.image_data.original_image=fn(self.image_data.original_image)
        self.render();self.canvas.fit_to_window()

    def geometry_dialog(self):
        if not self.layers:return
        choice,ok=QInputDialog.getItem(self,"Crop / Geometry","Operation",["Crop by pixels","Rotate 90°","Rotate 180°","Rotate 270°","Flip Horizontal","Flip Vertical"],0,False)
        if not ok:return
        if choice=="Crop by pixels":
            h,w=self.layers.active.pixels.shape[:2]
            vals=[]
            for label,default,limit in [("X",0,w-1),("Y",0,h-1),("Width",w,w),("Height",h,h)]:
                v,good=QInputDialog.getInt(self,"Crop / Geometry",label,default,1 if label in ("Width","Height") else 0,limit); 
                if not good:return
                vals.append(v)
            x,y,cw,ch=vals;self._transform_all_layers(lambda a:crop_array(a,x,y,cw,ch))
        else:
            rot={"Rotate 90°":90,"Rotate 180°":180,"Rotate 270°":270}.get(choice,0)
            self._transform_all_layers(lambda a:transform_array(a,rot,choice=="Flip Horizontal",choice=="Flip Vertical"))

    def typography_studio(self):
        if not self.layers:return
        if not self.text_overlays:
            text,ok=QInputDialog.getText(self,"Typography Studio","Text / العربية")
            if not ok or not text:return
            ov=TextOverlay(text,"Segoe UI",64,False,False,"#FFFFFF",.5,.5,1.0)
            ov.stroke_color="#000000";ov.stroke_width=0;ov.shadow=True;ov.rotation=0
            self.text_overlays.append(ov)
        ov=self.text_overlays[-1]
        d=QDialog(self);d.setWindowTitle("Typography Studio");form=QFormLayout(d)
        size=QSpinBox();size.setRange(8,400);size.setValue(int(ov.size));form.addRow("Size",size)
        x=QDoubleSpinBox();x.setRange(0,1);x.setSingleStep(.01);x.setValue(ov.x);form.addRow("X",x)
        y=QDoubleSpinBox();y.setRange(0,1);y.setSingleStep(.01);y.setValue(ov.y);form.addRow("Y",y)
        rot=QDoubleSpinBox();rot.setRange(-180,180);rot.setValue(float(getattr(ov,"rotation",0)));form.addRow("Rotation",rot)
        stroke=QSpinBox();stroke.setRange(0,30);stroke.setValue(int(getattr(ov,"stroke_width",0)));form.addRow("Stroke",stroke)
        shadow=QCheckBox();shadow.setChecked(bool(getattr(ov,"shadow",False)));form.addRow("Shadow",shadow)
        bold=QCheckBox();bold.setChecked(ov.bold);form.addRow("Bold",bold)
        italic=QCheckBox();italic.setChecked(ov.italic);form.addRow("Italic",italic)
        box=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);box.accepted.connect(d.accept);box.rejected.connect(d.reject);form.addRow(box)
        if d.exec():
            ov.size=size.value();ov.x=x.value();ov.y=y.value();ov.rotation=rot.value();ov.stroke_width=stroke.value();ov.shadow=shadow.isChecked();ov.bold=bold.isChecked();ov.italic=italic.isChecked();self.canvas.text_overlays=self.text_overlays;self.canvas.update();self.render()

    def export_studio(self):
        if not self.layers:return
        d=QDialog(self);d.setWindowTitle("Export Studio");form=QFormLayout(d)
        path,_=QFileDialog.getSaveFileName(self,"Export Studio","", "JPEG (*.jpg *.jpeg);;PNG (*.png);;TIFF (*.tif *.tiff)")
        if not path:return
        quality=QSpinBox();quality.setRange(1,100);quality.setValue(int(self.settings.get("default_jpeg_quality",95)));form.addRow("JPEG Quality",quality)
        h,w=self.layers.composite().shape[:2];width=QSpinBox();width.setRange(1,30000);width.setValue(w);height=QSpinBox();height.setRange(1,30000);height.setValue(h);form.addRow("Width",width);form.addRow("Height",height)
        keep=QCheckBox("Keep aspect ratio");keep.setChecked(True);form.addRow(keep)
        box=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);box.accepted.connect(d.accept);box.rejected.connect(d.reject);form.addRow(box)
        if d.exec():
            out_h=height.value();out_w=width.value()
            if keep.isChecked():out_h=max(1,round(h*out_w/w))
            try:export_image(self.layers.composite(),path,quality=quality.value(),width=out_w,height=out_h);self.info.setText(f"Exported: {Path(path).name}")
            except Exception as e:QMessageBox.critical(self,"Export Studio",str(e))

    def performance_dialog(self):
        d=QDialog(self);d.setWindowTitle("Performance / Preview");form=QFormLayout(d)
        side=QSpinBox();side.setRange(512,6000);side.setValue(self.preview_max_side);form.addRow("Preview max side",side)
        form.addRow(QLabel("ALIS keeps final rendering/export at full resolution. The preview ceiling is stored for the professional pipeline and future threaded preview workers."))
        box=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);box.accepted.connect(d.accept);box.rejected.connect(d.reject);form.addRow(box)
        if d.exec():self.preview_max_side=side.value();self.info.setText(f"Preview target set to {self.preview_max_side}px.")

    def _render_text_overlays(self,image):
        if not self.text_overlays:return image
        arr=np.ascontiguousarray(np.clip(image*255,0,255).astype(np.uint8));h,w=arr.shape[:2]
        q=QImage(arr.data,w,h,w*3,QImage.Format_RGB888).copy();p=QPainter(q);p.setRenderHint(QPainter.Antialiasing)
        for ov in self.text_overlays:
            font=QFont(ov.font_family,int(ov.size));font.setBold(bool(ov.bold));font.setItalic(bool(ov.italic));p.setFont(font)
            rect=QRectF(0,ov.y*h-ov.size*1.2,w,ov.size*2.4);p.save();p.translate(ov.x*w,ov.y*h);p.rotate(float(getattr(ov,"rotation",0)));p.translate(-ov.x*w,-ov.y*h)
            if getattr(ov,"shadow",False):
                p.setPen(QColor(0,0,0,150));p.drawText(rect.translated(4,4),Qt.AlignCenter,ov.text)
            sw=int(getattr(ov,"stroke_width",0))
            if sw>0:
                p.setPen(QColor(getattr(ov,"stroke_color","#000000")));p.drawText(rect,Qt.AlignCenter,ov.text)
            col=QColor(ov.color);col.setAlphaF(max(0,min(1,float(ov.opacity))));p.setPen(col);p.drawText(rect,Qt.AlignCenter,ov.text);p.restore()
        p.end();bits=q.bits();out=np.frombuffer(bits,np.uint8).reshape((h,q.bytesPerLine()//3,3))[:,:w,:].copy();return out.astype(np.float32)/255.

    def save_project(self):
        if not self.layers or not self.image_data:return
        p,_=QFileDialog.getSaveFileName(self,"Save Project","", "ALIS DEJA VU Project (*.alis)")
        if not p:return
        try:
            temp=copy.deepcopy(self.layers);temp.layers[0].pixels=self.image_data.original_image.copy()
            texts=[]
            for o in self.text_overlays:
                texts.append({k:getattr(o,k) for k in ("text","font_family","size","bold","italic","color","x","y","opacity")}|{"rotation":getattr(o,"rotation",0),"stroke_width":getattr(o,"stroke_width",0),"stroke_color":getattr(o,"stroke_color","#000000"),"shadow":getattr(o,"shadow",False)})
            metadata={"app_version":APP_VERSION,"advanced":self.advanced,"pro_grade":self.pro_grade,"pro_effects":self.pro_effects,"text_overlays":texts}
            ProjectFile.save(p,self.image_data.file_path,self.adjustments,temp,metadata)
            self.statusBar().showMessage(f"Project saved: {Path(p).name}")
        except Exception as e:
            self.logger.exception("Project save failed");QMessageBox.critical(self,"Save Project failed",str(e))

    def open_project(self):
        p,_=QFileDialog.getOpenFileName(self,"Open Project","", "ALIS DEJA VU Project (*.alis)")
        if not p:return
        try:
            import json,zipfile
            with zipfile.ZipFile(p) as z:manifest=json.loads(z.read("manifest.json").decode("utf-8"))
            original=Path(manifest["original_path"])
            if not original.exists():
                QMessageBox.warning(self,"Original image missing",f"The project references:\n{original}\n\nMove the original image back to this path before opening the project.");return
            self.image_data=ImageData(str(original));_,self.layers=ProjectFile.load(p,LayerStack,Mask,BlendMode)
            self.adjustments.update(manifest.get("adjustments",{}));meta=manifest.get("metadata",{});self.advanced.update(meta.get("advanced",{}));self.pro_grade.update(meta.get("pro_grade",{}));self.pro_effects.update(meta.get("pro_effects",{}))
            self.text_overlays=[]
            for d in meta.get("text_overlays",[]):
                o=TextOverlay(d.get("text",""),d.get("font_family","Segoe UI"),d.get("size",64),d.get("bold",False),d.get("italic",False),d.get("color","#FFFFFF"),d.get("x",.5),d.get("y",.5),d.get("opacity",1.0))
                for k in ("rotation","stroke_width","stroke_color","shadow"):
                    if k in d:setattr(o,k,d[k])
                self.text_overlays.append(o)
            self.canvas.text_overlays=self.text_overlays;self.undo.clear();self.refresh_layers();self.render();self.canvas.fit_to_window();self.setWindowTitle(f"{APP_NAME} — {Path(p).name}")
        except Exception as e:
            QMessageBox.critical(self,"Open Project failed",str(e))
