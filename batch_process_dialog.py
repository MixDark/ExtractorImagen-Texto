from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QListWidget, QListWidgetItem, QProgressBar,
                            QComboBox, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from config import ConfigManager
import os
from pathlib import Path

class BatchProcessThread(QThread):
    """Thread para procesar múltiples imágenes"""
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, image_paths, app_logic, export_format):
        super().__init__()
        self.image_paths = image_paths
        self.app_logic = app_logic
        self.export_format = export_format
        self.results = []
    
    def run(self):
        """Procesa las imágenes"""
        total = len(self.image_paths)
        
        for idx, image_path in enumerate(self.image_paths):
            try:
                self.status.emit(f"Procesando {idx + 1}/{total}: {os.path.basename(image_path)}")
                
                # Establecer la ruta de la imagen
                self.app_logic.set_image_path(image_path)
                
                # Extraer texto
                text = self.app_logic.extract_text()
                
                # Guardar en el formato especificado
                base_name = Path(image_path).stem
                output_dir = os.path.expanduser("~/Documents")
                
                if self.export_format == "docx":
                    output_path = os.path.join(output_dir, f"{base_name}.docx")
                    result_path = self.app_logic.save_text_to_docx(text)
                elif self.export_format == "txt":
                    output_path = os.path.join(output_dir, f"{base_name}.txt")
                    result_path = self.app_logic.save_text_to_txt(text, output_path)
                elif self.export_format == "pdf":
                    output_path = os.path.join(output_dir, f"{base_name}.pdf")
                    result_path = self.app_logic.save_text_to_pdf(text, output_path)
                elif self.export_format == "rtf":
                    output_path = os.path.join(output_dir, f"{base_name}.rtf")
                    result_path = self.app_logic.save_text_to_rtf(text, output_path)
                
                if result_path:
                    self.results.append({
                        'image': image_path,
                        'output': result_path,
                        'characters': len(''.join(text))
                    })
                
                progress_value = int((idx + 1) / total * 100)
                self.progress.emit(progress_value)
                
            except Exception as e:
                self.error.emit(f"Error procesando {os.path.basename(image_path)}: {str(e)}")
        
        self.finished.emit(self.results)


class BatchProcessDialog(QDialog):
    """Diálogo para procesamiento por lotes"""
    
    def __init__(self, app_logic, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesamiento por lotes")
        self.setGeometry(100, 100, 700, 500)
        self.app_logic = app_logic
        self.image_paths = []
        self.processing = False
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
            QListWidget {
                background-color: #2D2D2D;
                color: #FFFFFF;
                border: 1px solid #3D3D3D;
            }
            QListWidget::item:selected {
                background-color: #00BFFF;
                color: #000000;
            }
            QProgressBar {
                background-color: #2D2D2D;
                border: 1px solid #3D3D3D;
                border-radius: 4px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #00BFFF;
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
            QListWidget {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #E1E5EA;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QProgressBar {
                background-color: #F5F7FA;
                border: 1px solid #E1E5EA;
                border-radius: 4px;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
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
                background-color: #E0E0E0;
                color: #333333;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            """
        
        self.setStyleSheet(stylesheet)
    
    def setup_ui(self):
        """Configura la interfaz"""
        layout = QVBoxLayout(self)
        
        # Título
        title = QLabel("Procesar múltiples imágenes")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Lista de archivos
        layout.addWidget(QLabel("Imágenes a procesar:"))
        self.file_list = QListWidget()
        layout.addWidget(self.file_list)
        
        # Formato de exportación
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato de salida:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["DOCX", "TXT", "PDF", "RTF"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Estado
        self.status_label = QLabel("Listo para procesar")
        layout.addWidget(self.status_label)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Agregar imágenes")
        add_btn.setMinimumWidth(130)
        add_btn.clicked.connect(self.add_images)
        
        remove_btn = QPushButton("- Remover seleccionada")
        remove_btn.setMinimumWidth(140)
        remove_btn.clicked.connect(self.remove_image)
        
        clear_btn = QPushButton("Limpiar lista")
        clear_btn.setMinimumWidth(110)
        clear_btn.clicked.connect(self.clear_list)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.close)
        
        self.process_btn = QPushButton("▶ Procesar")
        self.process_btn.setMinimumWidth(100)
        self.process_btn.clicked.connect(self.process_batch)
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(remove_btn)
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(self.process_btn)
        
        layout.addLayout(buttons_layout)
    
    def add_images(self):
        """Abre diálogo para seleccionar imágenes"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar imágenes",
            "",
            "Imágenes (*.jpg *.jpeg *.png *.bmp *.gif *.tiff)"
        )
        
        for file_path in files:
            if file_path not in self.image_paths:
                self.image_paths.append(file_path)
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.file_list.addItem(item)
    
    def remove_image(self):
        """Remueve la imagen seleccionada"""
        current_item = self.file_list.currentItem()
        if current_item:
            index = self.file_list.row(current_item)
            self.image_paths.pop(index)
            self.file_list.takeItem(index)
    
    def clear_list(self):
        """Limpia la lista"""
        reply = QMessageBox.question(self, "Confirmar",
                                     "¿Deseas limpiar la lista?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.image_paths.clear()
            self.file_list.clear()
    
    def process_batch(self):
        """Inicia el procesamiento por lotes"""
        if not self.image_paths:
            QMessageBox.warning(self, "Error", "Debes agregar al menos una imagen")
            return
        
        self.processing = True
        self.process_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        export_format = self.format_combo.currentText().lower()
        
        self.batch_thread = BatchProcessThread(
            self.image_paths,
            self.app_logic,
            export_format
        )
        self.batch_thread.progress.connect(self.update_progress)
        self.batch_thread.status.connect(self.update_status)
        self.batch_thread.finished.connect(self.batch_finished)
        self.batch_thread.error.connect(self.batch_error)
        self.batch_thread.start()
    
    def update_progress(self, value):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(value)
    
    def update_status(self, status_text):
        """Actualiza el estado"""
        self.status_label.setText(status_text)
    
    def batch_finished(self, results):
        """Se ejecuta cuando el procesamiento termina"""
        self.processing = False
        self.process_btn.setEnabled(True)
        
        if results:
            message = f"Procesamiento completado:\n\n"
            message += f"Archivos procesados: {len(results)}\n"
            total_chars = sum(r['characters'] for r in results)
            message += f"Total de caracteres: {total_chars:,}\n\n"
            message += "Archivos guardados en Documentos"
            
            QMessageBox.information(self, "Éxito", message)
        else:
            QMessageBox.warning(self, "Error", "No se procesó ningún archivo")
        
        self.progress_bar.hide()
        self.status_label.setText("Listo para procesar")
    
    def batch_error(self, error_message):
        """Maneja errores durante el procesamiento"""
        QMessageBox.warning(self, "Error", error_message)
