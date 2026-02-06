from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTextEdit, QLabel, QSpinBox, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config import ConfigManager

class TextEditorDialog(QDialog):
    """Diálogo para editar el texto extraído"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editor de texto")
        self.setGeometry(100, 100, 800, 600)
        self.edited_text = text
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
            QTextEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                padding: 5px;
            }
            QSpinBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
            }
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                padding: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #2D2D2D;
                color: #FFFFFF;
                selection-background-color: #00BFFF;
            }
            QPushButton {
                background-color: #00BFFF;
                color: #000000;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
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
            QTextEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E1E5EA;
                padding: 5px;
            }
            QSpinBox {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E1E5EA;
            }
            QComboBox {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E1E5EA;
                padding: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #007AFF;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            """
        
        self.setStyleSheet(stylesheet)    
    def setup_ui(self):
        """Configura la interfaz del editor"""
        layout = QVBoxLayout(self)
        
        # Información
        text = self.edited_text
        info_label = QLabel(f"Texto extraído: {len(text)} caracteres en {len(text.split())} palabras")
        layout.addWidget(info_label)
        
        # Editor de texto
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(text)
        self.text_edit.setFont(QFont("Courier", 11))
        layout.addWidget(self.text_edit)
        
        # Barra de herramientas
        toolbar_layout = QHBoxLayout()
        
        # Tamaño de fuente
        size_label = QLabel("Tamaño:")
        self.font_size = QSpinBox()
        self.font_size.setValue(11)
        self.font_size.setMinimum(8)
        self.font_size.setMaximum(24)
        self.font_size.valueChanged.connect(self.change_font_size)
        
        # Familia de fuente
        font_label = QLabel("Fuente:")
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Courier", "Arial", "Times New Roman", "Verdana", "Monospace"])
        self.font_combo.currentTextChanged.connect(self.change_font_family)
        
        toolbar_layout.addWidget(font_label)
        toolbar_layout.addWidget(self.font_combo)
        toolbar_layout.addWidget(size_label)
        toolbar_layout.addWidget(self.font_size)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Botones inferiores
        buttons_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Limpiar")
        clear_btn.clicked.connect(self.clear_text)
        
        copy_btn = QPushButton("Copiar al portapapeles")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Guardar Cambios")
        save_btn.setStyleSheet("background-color: #007AFF; color: white; padding: 5px; font-weight: bold;")
        save_btn.clicked.connect(self.accept_changes)
        
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addWidget(copy_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def change_font_size(self, size):
        """Cambia el tamaño de la fuente"""
        font = self.text_edit.font()
        font.setPointSize(size)
        self.text_edit.setFont(font)
    
    def change_font_family(self, family):
        """Cambia la familia de la fuente"""
        font = self.text_edit.font()
        font.setFamily(family)
        self.text_edit.setFont(font)
    
    def clear_text(self):
        """Limpia todo el texto"""
        reply = QMessageBox.question(self, "Confirmar", 
                                     "¿Estás seguro de que deseas limpiar todo el texto?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.text_edit.clear()
    
    def copy_to_clipboard(self):
        """Copia el texto al portapapeles"""
        from utils import ClipboardManager
        text = self.text_edit.toPlainText()
        if ClipboardManager.copy_text(text):
            QMessageBox.information(self, "Éxito", "Texto copiado al portapapeles")
        else:
            QMessageBox.warning(self, "Error", "No se pudo copiar al portapapeles")
    
    def accept_changes(self):
        """Acepta los cambios realizados"""
        self.edited_text = self.text_edit.toPlainText()
        self.accept()
    
    def get_edited_text(self):
        """Retorna el texto editado"""
        return self.edited_text
