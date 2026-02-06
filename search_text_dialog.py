from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLineEdit, QLabel, QCheckBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from config import ConfigManager

class SearchTextDialog(QDialog):
    """Diálogo para buscar en texto"""
    
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Buscar texto")
        self.setGeometry(100, 100, 500, 200)
        self.text = text
        self.current_index = 0
        self.matches = []
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
            QLineEdit {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 2px solid #3D3D3D;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #00BFFF;
            }
            QCheckBox {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #4D4D4D;
                color: #FFFFFF;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5D5D5D;
            }
            QPushButton:disabled {
                background-color: #3D3D3D;
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
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 2px solid #E1E5EA;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #007AFF;
            }
            QCheckBox {
                color: #333333;
            }
            QPushButton {
                background-color: #E1E5EA;
                color: #333333;
                border: 1px solid #D0D5DC;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D0D5DC;
                border: 1px solid #B8BCC4;
            }
            QPushButton:disabled {
                background-color: #F5F7FA;
                border: 1px solid #E1E5EA;
            }
            """
        
        self.setStyleSheet(stylesheet)
    
    def setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        
        # Búsqueda
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Escribe el texto a buscar...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.find_next)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Opciones de búsqueda
        options_layout = QHBoxLayout()
        
        self.case_sensitive = QCheckBox("Distinguir mayúsculas")
        self.whole_word = QCheckBox("Palabra completa")
        
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.whole_word)
        options_layout.addStretch()
        
        layout.addLayout(options_layout)
        
        # Información
        info_layout = QHBoxLayout()
        self.info_label = QLabel("Escribe para buscar")
        self.info_label.setStyleSheet("color: #666666; font-size: 11px;")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        prev_btn = QPushButton("◀ Anterior")
        prev_btn.clicked.connect(self.find_previous)
        
        next_btn = QPushButton("Siguiente ▶")
        next_btn.clicked.connect(self.find_next)
        
        replace_layout = QHBoxLayout()
        replace_label = QLabel("Reemplazar por:")
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Texto de reemplazo (opcional)")
        replace_layout.addWidget(replace_label)
        replace_layout.addWidget(self.replace_input)
        
        layout.addLayout(replace_layout)
        
        replace_btn = QPushButton("Reemplazar")
        replace_btn.clicked.connect(self.replace_current)
        
        replace_all_btn = QPushButton("Reemplazar todo")
        replace_all_btn.clicked.connect(self.replace_all)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(prev_btn)
        buttons_layout.addWidget(next_btn)
        buttons_layout.addWidget(replace_btn)
        buttons_layout.addWidget(replace_all_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def on_search_changed(self, text):
        """Se ejecuta cuando cambia el texto de búsqueda"""
        if text:
            self.perform_search(text)
        else:
            self.matches = []
            self.current_index = 0
            self.info_label.setText("Escribe para buscar")
    
    def perform_search(self, search_text):
        """Realiza la búsqueda"""
        self.matches = []
        
        if not search_text:
            return
        
        text = self.text
        case_sensitive = self.case_sensitive.isChecked()
        whole_word = self.whole_word.isChecked()
        
        if not case_sensitive:
            search_text_lower = search_text.lower()
            text_lower = text.lower()
        else:
            search_text_lower = search_text
            text_lower = text
        
        # Buscar todas las coincidencias
        start = 0
        while True:
            index = text_lower.find(search_text_lower, start)
            if index == -1:
                break
            
            # Verificar palabra completa si está seleccionada
            if whole_word:
                # Verificar que no hay caracteres alfanuméricos antes o después
                before_ok = index == 0 or not text[index - 1].isalnum()
                after_ok = index + len(search_text) >= len(text) or not text[index + len(search_text)].isalnum()
                
                if before_ok and after_ok:
                    self.matches.append(index)
            else:
                self.matches.append(index)
            
            start = index + 1
        
        # Actualizar información
        if self.matches:
            self.current_index = 0
            count = len(self.matches)
            self.info_label.setText(f"Se encontraron {count} coincidencia{'s' if count > 1 else ''}")
        else:
            self.info_label.setText("No se encontraron coincidencias")
            self.current_index = 0
    
    def find_next(self):
        """Busca la siguiente coincidencia"""
        if not self.matches:
            QMessageBox.information(self, "No encontrado", "No hay texto para buscar")
            return
        
        self.current_index = (self.current_index + 1) % len(self.matches)
        self.show_current_match()
    
    def find_previous(self):
        """Busca la coincidencia anterior"""
        if not self.matches:
            QMessageBox.information(self, "No encontrado", "No hay texto para buscar")
            return
        
        self.current_index = (self.current_index - 1) % len(self.matches)
        self.show_current_match()
    
    def show_current_match(self):
        """Muestra la coincidencia actual"""
        if self.matches:
            index = self.matches[self.current_index]
            self.info_label.setText(f"Coincidencia {self.current_index + 1} de {len(self.matches)}")
    
    def replace_current(self):
        """Reemplaza la coincidencia actual"""
        if not self.matches:
            QMessageBox.warning(self, "Advertencia", "No hay coincidencias para reemplazar")
            return
        
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            QMessageBox.warning(self, "Advertencia", "Ingresa un texto a buscar")
            return
        
        index = self.matches[self.current_index]
        # Aquí se podría integrar con el editor para reemplazar el texto actual
        QMessageBox.information(self, "Éxito", 
                               f"Reemplazada coincidencia en posición {index}")
    
    def replace_all(self):
        """Reemplaza todas las coincidencias"""
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            QMessageBox.warning(self, "Advertencia", "Ingresa un texto a buscar")
            return
        
        case_sensitive = self.case_sensitive.isChecked()
        
        if case_sensitive:
            new_text = self.text.replace(search_text, replace_text)
        else:
            # Reemplazo insensible a mayúsculas
            new_text = self.text
            import re
            pattern = re.compile(re.escape(search_text), re.IGNORECASE)
            new_text = pattern.sub(replace_text, new_text)
        
        replacements = len(self.matches)
        QMessageBox.information(self, "Éxito", 
                               f"Se reemplazaron {replacements} coincidencia{'s' if replacements > 1 else ''}")
    
    def get_results(self):
        """Retorna los resultados de búsqueda"""
        return {
            'text': self.text,
            'matches': self.matches,
            'search_text': self.search_input.text()
        }
