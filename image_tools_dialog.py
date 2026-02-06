from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QSlider, QMessageBox, QTabWidget, QWidget,
                            QSpinBox, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PIL import Image, ImageEnhance
from config import ConfigManager
import os

class ImageToolsDialog(QDialog):
    """Diálogo para herramientas de edición de imagen"""
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Herramientas de imagen")
        self.setGeometry(100, 100, 500, 400)
        self.image_path = image_path
        self.temp_path = "temp_edited.png"
        self.config_manager = ConfigManager()
        self.is_dark_theme = self.config_manager.get_theme() == "dark"
        self.setup_ui()
        self.apply_styles()
    
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
            QTabWidget {
                background-color: #1E1E1E;
            }
            QTabBar::tab {
                background-color: #2D2D2D;
                color: #FFFFFF;
                padding: 8px 15px;
                border: 1px solid #3D3D3D;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                color: #00BFFF;
                border-bottom: 3px solid #00BFFF;
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
            QSpinBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
            }
            QPushButton {
                background-color: #00BFFF;
                color: #000000;
                border: none;
                padding: 6px 12px;
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
            QTabWidget {
                background-color: #FFFFFF;
            }
            QTabBar::tab {
                background-color: #F5F7FA;
                color: #333333;
                padding: 8px 15px;
                border: 1px solid #E1E5EA;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #007AFF;
                border-bottom: 3px solid #007AFF;
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
            QSpinBox {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E1E5EA;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
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
        title = QLabel("Herramientas de edición de imagen")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab de Rotación
        rotation_widget = self.create_rotation_tab()
        tabs.addTab(rotation_widget, "Rotación")
        
        # Tab de Brillo y Contraste
        brightness_widget = self.create_brightness_contrast_tab()
        tabs.addTab(brightness_widget, "Brillo/Contraste")
        
        layout.addWidget(tabs)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Restaurar original")
        reset_btn.clicked.connect(self.reset_image)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        apply_btn = QPushButton("✓ Aplicar cambios")
        apply_btn.setStyleSheet("background-color: #007AFF; color: white; min-width: 100px; font-weight: bold;")
        apply_btn.clicked.connect(self.apply_changes)
        
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(apply_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_rotation_tab(self):
        """Crea la pestaña de rotación"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Ángulo de rotación:"))
        
        # Controles de rotación rápida
        quick_layout = QHBoxLayout()
        
        for angle in [-90, -45, 45, 90]:
            btn = QPushButton(f"{angle}°")
            btn.clicked.connect(lambda checked, a=angle: self.rotate_quick(a))
            quick_layout.addWidget(btn)
        
        layout.addLayout(quick_layout)
        
        # Slider personalizado
        layout.addWidget(QLabel("Rotación personalizada:"))
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal)
        self.rotation_slider.setMinimum(-180)
        self.rotation_slider.setMaximum(180)
        self.rotation_slider.setValue(0)
        self.rotation_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rotation_slider.setTickInterval(10)
        layout.addWidget(self.rotation_slider)
        
        # Mostrar valor actual
        self.rotation_label = QLabel("0°")
        self.rotation_slider.valueChanged.connect(self.update_rotation_label)
        layout.addWidget(self.rotation_label)
        
        layout.addStretch()
        return widget
    
    def create_brightness_contrast_tab(self):
        """Crea la pestaña de brillo y contraste"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Brillo
        layout.addWidget(QLabel("Brillo:"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setMinimum(0)
        self.brightness_slider.setMaximum(200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.brightness_slider.setTickInterval(10)
        layout.addWidget(self.brightness_slider)
        
        self.brightness_label = QLabel("100%")
        self.brightness_slider.valueChanged.connect(self.update_brightness_label)
        layout.addWidget(self.brightness_label)
        
        layout.addSpacing(20)
        
        # Contraste
        layout.addWidget(QLabel("Contraste:"))
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setMinimum(0)
        self.contrast_slider.setMaximum(200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.contrast_slider.setTickInterval(10)
        layout.addWidget(self.contrast_slider)
        
        self.contrast_label = QLabel("100%")
        self.contrast_slider.valueChanged.connect(self.update_contrast_label)
        layout.addWidget(self.contrast_label)
        
        layout.addSpacing(20)
        
        # Saturación
        layout.addWidget(QLabel("Saturación:"))
        self.saturation_slider = QSlider(Qt.Orientation.Horizontal)
        self.saturation_slider.setMinimum(0)
        self.saturation_slider.setMaximum(200)
        self.saturation_slider.setValue(100)
        self.saturation_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.saturation_slider.setTickInterval(10)
        layout.addWidget(self.saturation_slider)
        
        self.saturation_label = QLabel("100%")
        self.saturation_slider.valueChanged.connect(self.update_saturation_label)
        layout.addWidget(self.saturation_label)
        
        layout.addStretch()
        return widget
    
    def update_rotation_label(self, value):
        """Actualiza la etiqueta de rotación"""
        self.rotation_label.setText(f"{value}°")
    
    def update_brightness_label(self, value):
        """Actualiza la etiqueta de brillo"""
        percent = int((value / 100) * 100)
        self.brightness_label.setText(f"{percent}%")
    
    def update_contrast_label(self, value):
        """Actualiza la etiqueta de contraste"""
        percent = int((value / 100) * 100)
        self.contrast_label.setText(f"{percent}%")
    
    def update_saturation_label(self, value):
        """Actualiza la etiqueta de saturación"""
        percent = int((value / 100) * 100)
        self.saturation_label.setText(f"{percent}%")
    
    def rotate_quick(self, angle):
        """Rota rápidamente"""
        current = self.rotation_slider.value()
        self.rotation_slider.setValue(current + angle)
    
    def reset_image(self):
        """Restaura la imagen original"""
        self.rotation_slider.setValue(0)
        self.brightness_slider.setValue(100)
        self.contrast_slider.setValue(100)
        self.saturation_slider.setValue(100)
        QMessageBox.information(self, "Restaurado", "Imagen restaurada a valores originales")
    
    def apply_changes(self):
        """Aplica los cambios a la imagen"""
        try:
            # Cargar imagen original
            image = Image.open(self.image_path)
            
            # Aplicar rotación
            angle = self.rotation_slider.value()
            if angle != 0:
                image = image.rotate(angle, expand=True, fillcolor='white')
            
            # Aplicar brillo
            brightness_factor = self.brightness_slider.value() / 100.0
            if brightness_factor != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness_factor)
            
            # Aplicar contraste
            contrast_factor = self.contrast_slider.value() / 100.0
            if contrast_factor != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast_factor)
            
            # Aplicar saturación
            saturation_factor = self.saturation_slider.value() / 100.0
            if saturation_factor != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(saturation_factor)
            
            # Guardar cambios
            image.save(self.image_path)
            QMessageBox.information(self, "Éxito", "Cambios aplicados a la imagen")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar imagen: {e}")
