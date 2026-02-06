from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QTabWidget, QWidget, QListWidget, QListWidgetItem,
                            QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from datetime import datetime

class StatisticsDialog(QDialog):
    """Diálogo para mostrar estadísticas"""
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("Estadísticas y configuración")
        self.setGeometry(100, 100, 600, 500)
        
        # Detectar el tema
        self.is_dark_theme = self.config_manager.get_theme() == "dark"
        
        self.setup_ui()
        self.apply_dialog_styles()
    
    def apply_dialog_styles(self):
        """Aplica estilos específicos al diálogo según el tema"""
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
                padding: 8px 20px;
                border: 1px solid #3D3D3D;
            }
            QTabBar::tab:selected {
                background-color: #1E1E1E;
                color: #00BFFF;
                border-bottom: 3px solid #00BFFF;
            }
            QTabWidget::pane {
                border: 1px solid #3D3D3D;
            }
            QListWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
            }
            QListWidget::item:selected {
                background-color: #00BFFF;
                color: #000000;
            }
            QComboBox {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
                padding: 4px;
            }
            QComboBox::drop-down {
                background-color: #2D2D2D;
            }
            QComboBox QAbstractItemView {
                background-color: #2D2D2D;
                color: #FFFFFF;
                selection-background-color: #00BFFF;
            }
            QPushButton {
                background-color: #3D3D3D;
                color: #FFFFFF;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4D4D4D;
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
                padding: 8px 20px;
                border: 1px solid #E1E5EA;
            }
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #007AFF;
                border-bottom: 3px solid #007AFF;
            }
            QTabWidget::pane {
                border: 1px solid #E1E5EA;
            }
            QListWidget {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E1E5EA;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QComboBox {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E1E5EA;
                padding: 4px;
            }
            QComboBox::drop-down {
                background-color: #FFFFFF;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #007AFF;
            }
            QPushButton {
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            """
        
        self.setStyleSheet(stylesheet)
    
    def setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab de estadísticas
        stats_widget = self.create_statistics_tab()
        tabs.addTab(stats_widget, "Estadísticas")
        
        # Tab de historial
        history_widget = self.create_history_tab()
        tabs.addTab(history_widget, "Historial")
        
        # Tab de configuración
        config_widget = self.create_config_tab()
        tabs.addTab(config_widget, "Configuración")
        
        layout.addWidget(tabs)
        
        # Botones
        buttons_layout = QHBoxLayout()
        close_btn = QPushButton("Cerrar")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.accept)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_statistics_tab(self):
        """Crea la pestaña de estadísticas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        stats = self.config_manager.get_statistics()
        
        # Información
        info_texts = [
            f"📊 Total de caracteres extraídos: {stats.get('total_characters', 0):,}",
            f"📁 Archivos procesados: {stats.get('files_processed', 0)}",
            f"⏱️  Tiempo total de procesamiento: {stats.get('total_processing_time', 0):.2f}s"
        ]
        
        if stats.get('files_processed', 0) > 0:
            avg_time = stats.get('total_processing_time', 0) / stats.get('files_processed', 0)
            avg_chars = stats.get('total_characters', 0) / stats.get('files_processed', 0)
            info_texts.extend([
                f"⚡ Tiempo promedio por archivo: {avg_time:.2f}s",
                f"📝 Promedio de caracteres por archivo: {avg_chars:.0f}"
            ])
        
        for text in info_texts:
            label = QLabel(text)
            label.setStyleSheet("font-size: 14px; margin: 10px;")
            layout.addWidget(label)
        
        layout.addStretch()
        
        # Botón para limpiar
        clear_btn = QPushButton("Limpiar estadísticas")
        clear_btn.setMinimumWidth(140)
        clear_btn.clicked.connect(self.clear_statistics)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        return widget
    
    def create_history_tab(self):
        """Crea la pestaña de historial"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Últimos archivos procesados:"))
        
        # Lista de archivos recientes
        self.history_list = QListWidget()
        recent_files = self.config_manager.get_recent_files()
        
        if not recent_files:
            self.history_list.addItem("No hay archivos recientes")
        else:
            for file_info in recent_files:
                timestamp = file_info.get('timestamp', '')
                path = file_info.get('path', '')
                chars = file_info.get('characters', 0)
                
                # Parsear timestamp
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime("%d/%m/%Y %H:%M")
                except:
                    time_str = timestamp
                
                item_text = f"{path}\n{time_str} | {chars} caracteres"
                item = QListWidgetItem(item_text)
                self.history_list.addItem(item)
        
        layout.addWidget(self.history_list)
        
        # Botón para limpiar historial
        clear_history_btn = QPushButton("Limpiar historial")
        clear_history_btn.setMaximumWidth(200)
        clear_history_btn.clicked.connect(self.clear_history)
        btn_layout2 = QHBoxLayout()
        btn_layout2.addStretch()
        btn_layout2.addWidget(clear_history_btn)
        btn_layout2.addStretch()
        layout.addLayout(btn_layout2)
        
        return widget
    
    def create_config_tab(self):
        """Crea la pestaña de configuración"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tema
        theme_label = QLabel("Tema:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Oscuro"])
        current_theme = self.config_manager.get_theme()
        if current_theme == "dark":
            self.theme_combo.setCurrentIndex(1)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Formato de exportación por defecto
        format_label = QLabel("Formato de exportación predeterminado:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["DOCX", "TXT", "PDF", "RTF"])
        default_format = self.config_manager.get("default_export_format", "docx").upper()
        self.format_combo.setCurrentText(default_format)
        self.format_combo.currentTextChanged.connect(self.change_format)
        
        format_layout = QHBoxLayout()
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        layout.addStretch()
        
        return widget
    
    def clear_statistics(self):
        """Limpia las estadísticas"""
        reply = QMessageBox.question(self, "Confirmar",
                                     "¿Deseas limpiar todas las estadísticas?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.config["statistics"] = {
                "total_characters": 0,
                "files_processed": 0,
                "total_processing_time": 0
            }
            self.config_manager.save_config()
            QMessageBox.information(self, "Éxito", "Estadísticas limpiadas")
            # Actualizar la vista
            self.setup_ui()
    
    def clear_history(self):
        """Limpia el historial"""
        reply = QMessageBox.question(self, "Confirmar",
                                     "¿Deseas limpiar el historial?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.clear_recent()
            QMessageBox.information(self, "Éxito", "Historial limpiado")
            self.history_list.clear()
            self.history_list.addItem("No hay archivos recientes")
    
    def change_theme(self, theme):
        """Cambia el tema"""
        theme_value = "dark" if theme == "Oscuro" else "light"
        self.config_manager.set_theme(theme_value)
        QMessageBox.information(self, "Tema", 
                               "El tema se cambiará cuando reinicies la aplicación")
    
    def change_format(self, format_type):
        """Cambia el formato de exportación predeterminado"""
        self.config_manager.set("default_export_format", format_type.lower())
