from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSlider, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QImage, QPixmap, QFont
from config import ConfigManager
import cv2
import numpy as np
import time
import os

class CameraThread(QThread):
    """Thread para capturar video de la cámara"""
    frame_ready = pyqtSignal(QImage)
    error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.camera = None
    
    def run(self):
        """Ejecuta el hilo de captura"""
        try:
            self.running = True
            # Usar CAP_DSHOW en Windows para mejor compatibilidad
            self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            
            if not self.camera.isOpened():
                self.error_signal.emit("No se pudo abrir la cámara. Intenta: 1) reconectar la cámara, 2) reiniciar la app")
                return
            
            # Configurar propiedades de la cámara
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimizar buffer
            
            # Buffer para calentar la cámara
            warmup_count = 0
            while self.running and warmup_count < 10:
                ret, frame = self.camera.read()
                if ret:
                    warmup_count += 1
                time.sleep(0.05)
            
            if warmup_count == 0:
                self.error_signal.emit("La cámara no responde. Intenta reconectarla.")
                return
            
            frame_count = 0
            while self.running:
                ret, frame = self.camera.read()
                if ret and frame is not None:
                    try:
                        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # Asegurar que el frame es contiguo en memoria
                        rgb_frame = cv2.UMat(rgb_frame).get()  # Convertir a numpy array contiguo
                        h, w, ch = rgb_frame.shape
                        bytes_per_line = 3 * w
                        # Crear una copia segura del data
                        image_data = rgb_frame.tobytes()
                        qt_image = QImage(image_data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                        self.frame_ready.emit(qt_image)
                        frame_count += 1
                        time.sleep(0.033)  # ~30 FPS
                    except Exception as e:
                        print(f"Error procesando frame: {e}")
                else:
                    # Si falla una lectura, esperar y reintentar
                    time.sleep(0.1)
                    
        except Exception as e:
            self.error_signal.emit(f"Error en cámara: {str(e)}")
    
    def stop(self):
        """Detiene la captura"""
        self.running = False
        if self.camera:
            self.camera.release()
        self.wait()


class CameraDialog(QDialog):
    """Diálogo para capturar foto desde cámara"""
    
    photo_captured = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Capturar desde Cámara")
        self.setGeometry(100, 100, 800, 600)
        self.captured_image = None
        self.current_frame = None
        self.config_manager = ConfigManager()
        self.is_dark_theme = self.config_manager.get_theme() == "dark"
        self.setup_ui()
        self.apply_styles()
        
        # Iniciar la cámara
        self.camera_thread = CameraThread()
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.error_signal.connect(self.handle_camera_error)
        self.camera_thread.start()
    
    def apply_styles(self):
        """Aplica estilos al diálogo según el tema"""
        if self.is_dark_theme:
            stylesheet = """
            QDialog {
                background-color: #1E1E1E;
            }
            QLabel {
                color: #FFFFFF;
            }
            QSlider {
                background-color: #1E1E1E;
            }
            QSlider::groove:horizontal {
                background-color: #3D3D3D;
                height: 5px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #00BFFF;
                width: 15px;
                height: 15px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QPushButton {
                background-color: #00BFFF;
                color: #000000;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0099CC;
            }
            """
        else:
            stylesheet = """
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #333333;
            }
            QSlider {
                background-color: #FFFFFF;
            }
            QSlider::groove:horizontal {
                background-color: #E1E5EA;
                height: 5px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background-color: #007AFF;
                width: 15px;
                height: 15px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            """
        
        self.setStyleSheet(stylesheet)
    
    def setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Vista de la cámara")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Widget para mostrar la cámara
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("border: 2px solid #007AFF; background-color: #000000;")
        layout.addWidget(self.camera_label)
        
        # Controles de brillo y contraste (horizontal)
        controls_layout = QHBoxLayout()
        
        # Brillo
        brightness_label = QLabel("Brillo:")
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.setMaximumWidth(150)
        
        # Contraste
        contrast_label = QLabel("Contraste:")
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(100)
        self.contrast_slider.setValue(50)
        self.contrast_slider.setMaximumWidth(150)
        
        controls_layout.addWidget(brightness_label)
        controls_layout.addWidget(self.brightness_slider)
        controls_layout.addWidget(contrast_label)
        controls_layout.addWidget(self.contrast_slider)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("❌ Cancelar")
        cancel_btn.setStyleSheet("background-color: #007AFF; color: white; padding: 10px; font-weight: bold;")
        cancel_btn.setText("✕ Cancelar")
        cancel_btn.clicked.connect(self.close)
        
        capture_btn = QPushButton("📷 Capturar")
        capture_btn.setStyleSheet("background-color: #007AFF; color: white; padding: 10px; font-weight: bold;")
        capture_btn.clicked.connect(self.capture_photo)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(capture_btn)
        
        layout.addLayout(buttons_layout)
    
    def update_frame(self, qt_image):
        """Actualiza el frame mostrado"""
        self.current_frame = qt_image
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.camera_label.setPixmap(scaled_pixmap)
    
    def handle_camera_error(self, error_msg):
        """Maneja errores de cámara"""
        QMessageBox.warning(self, "Error de Cámara", error_msg)
    
    def capture_photo(self):
        """Captura la foto actual"""
        if self.current_frame:
            try:
                self.captured_image = self.current_frame
                # Guardar en el directorio output o actual
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                temp_path = os.path.join(output_dir, "camera_capture.png")
                self.captured_image.save(temp_path)
                
                QMessageBox.information(self, "Éxito", "Foto capturada exitosamente")
                self.photo_captured.emit(temp_path)
                
                # Detener thread y aceptar el diálogo
                self.camera_thread.stop()
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar la foto: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "No se pudo capturar la foto")
    
    def closeEvent(self, event):
        """Limpia recursos al cerrar"""
        try:
            self.camera_thread.stop()
            self.camera_thread.wait(2000)  # Esperar máximo 2 segundos
        except:
            pass
        event.accept()
