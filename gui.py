import sys
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                            QMessageBox, QProgressBar, QMenuBar, QMenu, QScrollArea, QDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon, QKeySequence
from PIL import Image
from imagen_texto import TextExtractorApp
from config import ConfigManager
from utils import ClipboardManager, ImageProcessor, SecurityValidator, SecurityLogger
from text_editor_dialog import TextEditorDialog
from statistics_dialog import StatisticsDialog
from camera_dialog import CameraDialog
from batch_process_dialog import BatchProcessDialog
from image_tools_dialog import ImageToolsDialog
from search_text_dialog import SearchTextDialog

class ExtractionWorker(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    processing_time = pyqtSignal(float)

    def __init__(self, app_logic):
        super().__init__()
        self.app_logic = app_logic

    def run(self):
        try:
            start_time = time.time()
            self.progress.emit(20)
            result = self.app_logic.extract_text()
            self.progress.emit(100)
            elapsed_time = time.time() - start_time
            self.processing_time.emit(elapsed_time)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("actionButton")
        self._animation = QPropertyAnimation(self, b"geometry")
        self._animation.setDuration(100)
        self._animation.setEasingCurve(QEasingCurve.Type.OutQuad)

    def enterEvent(self, event):
        rect = self.geometry()
        self._animation.setStartValue(rect)
        self._animation.setEndValue(rect.adjusted(-2, -2, 2, 2))
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        rect = self.geometry()
        self._animation.setStartValue(rect)
        self._animation.setEndValue(rect.adjusted(2, 2, -2, -2))
        self._animation.start()
        super().leaveEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Inicializar con fallback seguro - intentar usar service container
        self.service_container = None
        try:
            from src.service_container import get_service_container
            self.service_container = get_service_container()
            SecurityLogger.log_invalid_input('service_container', 'Clean Architecture initialized')
        except ImportError:
            SecurityLogger.log_invalid_input('service_container', 'Clean Architecture not available, using legacy mode')
        
        # Inicializar servicios (con fallback a implementación directa)
        self.config_manager = ConfigManager()
        self.app_logic = TextExtractorApp()
        self.extracted_text = None
        self.current_processing_time = 0
        self.setWindowTitle("Extractor de imagen a texto")
        self.setWindowIcon(QIcon('icon.png'))
        self.apply_styles()  # Aplicar estilos primero
        self.setup_ui()
        self.setup_menu()
        self.setup_shortcuts()
        self.load_recent_files()  

    def setup_ui(self):
        self.setWindowTitle("Extractor de imagen a texto")
        self.setFixedSize(950, 760)

        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Contenedor para la imagen
        self.image_container = QWidget()
        self.image_container.setObjectName("imageContainer")
        image_layout = QVBoxLayout(self.image_container)

        # Área de imagen
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(720, 400)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setObjectName("imagePreview")

        # Label de instrucciones
        self.instruction_label = QLabel("Arrastra una imagen aquí o haz clic en 'Cargar'")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setObjectName("instructionLabel")

        image_layout.addWidget(self.image_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.instruction_label)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.hide()

        # Contenedor de botones principales (primera fila)
        button_container1 = QWidget()
        button_container1.setObjectName("buttonContainer")
        button_layout1 = QHBoxLayout(button_container1)
        button_layout1.setSpacing(10)
        button_layout1.setContentsMargins(10, 5, 10, 5)

        # Botones animados principales con tooltips
        self.load_button = AnimatedButton("📂 Cargar")
        self.load_button.setMinimumHeight(45)
        self.load_button.setToolTip("Cargar imagen desde archivo (Ctrl+O)")
        
        self.camera_button = AnimatedButton("📷 Cámara")
        self.camera_button.setMinimumHeight(45)
        self.camera_button.setToolTip("Capturar imagen desde cámara web")
        
        self.paste_button = AnimatedButton("📋 Pegar")
        self.paste_button.setMinimumHeight(45)
        self.paste_button.setToolTip("Pegar imagen desde portapapeles")
        
        self.extract_button = AnimatedButton("⭐ Extraer")
        self.extract_button.setMinimumHeight(45)
        self.extract_button.setToolTip("Extraer texto de la imagen (Ctrl+S)")

        for button in [self.load_button, self.camera_button, self.paste_button, self.extract_button]:
            button_layout1.addWidget(button)

        # Contenedor de botones secundarios (segunda fila)
        button_container2 = QWidget()
        button_container2.setObjectName("buttonContainer")
        button_layout2 = QHBoxLayout(button_container2)
        button_layout2.setSpacing(10)
        button_layout2.setContentsMargins(10, 5, 10, 5)

        # Botones adicionales con tooltips
        self.edit_button = AnimatedButton("✏️ Editar")
        self.edit_button.setMinimumHeight(45)
        self.edit_button.setToolTip("Editar el texto extraído")
        
        self.copy_button = AnimatedButton("📋 Copiar")
        self.copy_button.setMinimumHeight(45)
        self.copy_button.setToolTip("Copiar texto al portapapeles (Ctrl+C)")
        
        self.open_button = AnimatedButton("📄 Abrir")
        self.open_button.setMinimumHeight(45)
        self.open_button.setToolTip("Abrir documento guardado")
        
        self.batch_button = AnimatedButton("📚 Lotes")
        self.batch_button.setMinimumHeight(45)
        self.batch_button.setToolTip("Procesar múltiples imágenes")
        
        self.stats_button = AnimatedButton("📊 Estadísticas")
        self.stats_button.setMinimumHeight(45)
        self.stats_button.setToolTip("Ver estadísticas y configuración")

        for button in [self.edit_button, self.copy_button, self.open_button, self.batch_button, self.stats_button]:
            button_layout2.addWidget(button)

        # Contenedor de botones adicionales (tercera fila) - Herramientas
        button_container3 = QWidget()
        button_container3.setObjectName("buttonContainer")
        button_layout3 = QHBoxLayout(button_container3)
        button_layout3.setSpacing(10)
        button_layout3.setContentsMargins(10, 5, 10, 5)

        # Botones de herramientas
        self.tools_button = AnimatedButton("🛠️ Herramientas")
        self.tools_button.setMinimumHeight(45)
        self.tools_button.setToolTip("Editar brillo, contraste, rotación de imagen")
        
        self.search_button = AnimatedButton("🔍 Buscar")
        self.search_button.setMinimumHeight(45)
        self.search_button.setToolTip("Buscar texto en el contenido extraído (Ctrl+F)")
        
        # Agregar algunos espacios
        button_layout3.addWidget(self.tools_button)
        button_layout3.addWidget(self.search_button)
        button_layout3.addStretch()

        # Deshabilitar botones hasta que se cargue imagen
        self.extract_button.setEnabled(False)
        self.open_button.setEnabled(False)
        self.edit_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.tools_button.setEnabled(False)
        self.search_button.setEnabled(False)

        # Agregar widgets al layout principal
        main_layout.addWidget(self.image_container)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(button_container1)
        main_layout.addWidget(button_container2)
        main_layout.addWidget(button_container3)

        # Conectar señales de botones
        self.load_button.clicked.connect(self.load_image)
        self.camera_button.clicked.connect(self.capture_from_camera)
        self.paste_button.clicked.connect(self.paste_image_from_clipboard)
        self.extract_button.clicked.connect(self.extract_text_from_image)
        self.edit_button.clicked.connect(self.edit_text)
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.open_button.clicked.connect(self.open_document)
        self.batch_button.clicked.connect(self.process_batch)
        self.stats_button.clicked.connect(self.show_statistics)
        self.tools_button.clicked.connect(self.open_image_tools)
        self.search_button.clicked.connect(self.open_search_dialog)

        # Configurar drag and drop
        self.setAcceptDrops(True)

    def apply_styles(self):
        # Estilo moderno - cargado desde archivo externo
        try:
            theme = self.config_manager.get_theme()
            style_file = 'styles.qss'
            
            with open(style_file, 'r') as f:
                stylesheet = f.read()
            
            # Si es tema oscuro, invertir colores
            if theme == "dark":
                stylesheet = self.invert_stylesheet(stylesheet)
            
            self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            # Si el archivo no existe, usar estilos por defecto
            self.setStyleSheet("QMainWindow { background-color: #FFFFFF; }")
    
    def invert_stylesheet(self, stylesheet):
        """Invierte los colores del stylesheet para tema oscuro"""
        # Color mapping básico
        replacements = {
            '#FFFFFF': '#1E1E1E',  # Blanco a gris oscuro
            '#F5F7FA': '#2D2D2D',  # Fondo claro a gris oscuro
            '#333333': '#E0E0E0',  # Texto oscuro a texto claro
            '#007AFF': '#4A9EFF',  # Azul más brillante
            '#0056B3': '#0078D4',  # Azul más claro
            '#E1E5EA': '#404040',  # Borde claro a oscuro
            '#6B7280': '#B0B0B0',  # Texto gris a más claro
            '#C0C6CC': '#505050',  # Borde gris a más oscuro
            '#9CA3AF': '#808080',  # Texto deshabilitado
        }
        
        for light, dark in replacements.items():
            stylesheet = stylesheet.replace(light, dark)
        
        return stylesheet

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            try:
                # Validar archivo arrastrado
                is_valid, error = SecurityValidator.validate_image_path(files[0])
                if not is_valid:
                    SecurityLogger.log_invalid_input('dropEvent', error)
                    QMessageBox.critical(self, "Archivo inválido", f"Validación de seguridad rechazada: {error}")
                    return
                
                self.app_logic.set_image_path(files[0])
                self.show_image_preview()
                self.enable_extract_button()
                SecurityLogger.log_file_access(files[0], 'drag_drop')
            except Exception as e:
                SecurityLogger.log_invalid_input('dropEvent', str(e))
                QMessageBox.critical(self, "Error", f"Error al procesar archivo: {e}")

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen",
            "",
            "Imágenes (*.jpg *.jpeg *.png *.bmp *.gif)"
        )
        if file_name:
            try:
                # Validar ruta de imagen antes de procesarla
                is_valid, error = SecurityValidator.validate_image_path(file_name)
                if not is_valid:
                    SecurityLogger.log_invalid_input('load_image', error)
                    QMessageBox.critical(self, "Archivo inválido", f"Validación de seguridad rechazada: {error}")
                    return
                
                self.app_logic.set_image_path(file_name)
                self.show_image_preview()
                self.enable_extract_button()
                SecurityLogger.log_file_access(file_name, 'image_loaded')
            except Exception as e:
                SecurityLogger.log_invalid_input('load_image', str(e))
                QMessageBox.critical(self, "Error", f"Error al cargar la imagen: {e}")

    def show_image_preview(self):
        try:
            image = Image.open(self.app_logic.image_path)
            image.thumbnail((720, 400))
            image.save("temp.png")
            pixmap = QPixmap("temp.png")
            self.image_preview.setPixmap(pixmap)
            self.instruction_label.hide()
        except Exception as e:
            SecurityLogger.log_invalid_input('show_image_preview', str(e))
            QMessageBox.critical(self, "Error", f"Error al cargar la imagen: {e}")

    def enable_extract_button(self):
        self.extract_button.setEnabled(True)
        self.tools_button.setEnabled(True)

    def extract_text_from_image(self):
        """Extrae el texto de la imagen"""
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.extract_button.setEnabled(False)
        
        self.worker = ExtractionWorker(self.app_logic)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.handle_extraction_finished)
        self.worker.error.connect(self.handle_extraction_error)
        self.worker.processing_time.connect(self.save_processing_time)
        self.worker.start()
    
    def save_processing_time(self, elapsed_time):
        self.current_processing_time = elapsed_time

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def handle_extraction_finished(self, result):
        try:
            self.extracted_text = result
            # Actualizar estadísticas
            char_count = sum(len(p) for p in result)
            self.config_manager.add_to_recent(self.app_logic.image_path, char_count)
            self.config_manager.update_statistics(char_count, self.current_processing_time)
            
            # Mostrar opciones de exportación
            default_format = self.config_manager.get("default_export_format", "docx")
            self.show_export_options(result, default_format)
            
            self.open_button.setEnabled(True)
            self.edit_button.setEnabled(True)
            self.copy_button.setEnabled(True)
            self.search_button.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.extract_button.setEnabled(True)
            self.progress_bar.hide()

    def handle_extraction_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.extract_button.setEnabled(True)
        self.progress_bar.hide()
    
    def show_export_options(self, text, default_format="docx"):
        """Muestra opciones de exportación"""
        try:
            # Validar texto antes de exportar (OWASP A03)
            full_text = '\n'.join(text) if isinstance(text, list) else str(text)
            is_valid, error = SecurityValidator.validate_text_input(full_text)
            if not is_valid:
                SecurityLogger.log_invalid_input('export_text', error)
                QMessageBox.critical(self, "Texto inválido", f"Validación de seguridad rechazada: {error}")
                return
            
            result = QMessageBox.question(
                self,
                "Exportar Texto",
                "¿En qué formato deseas guardar?\n\nSe utilizará el formato predeterminado.",
                buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )
            
            if result == QMessageBox.StandardButton.Ok:
                # Guardar en formato predeterminado
                try:
                    format_type = default_format
                    self.app_logic.export_to_format(text, format_type)
                    SecurityLogger.log_export(self.app_logic.save_path or 'unknown', format_type, True)
                except ImportError as e:
                    QMessageBox.warning(self, "Dependencia", 
                                       f"Se requiere instalar reportlab para PDF: pip install reportlab")
                except Exception as e:
                    SecurityLogger.log_export(self.app_logic.save_path or 'unknown', default_format, False)
                    QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")
        except Exception as e:
            SecurityLogger.log_invalid_input('show_export_options', str(e))
            QMessageBox.critical(self, "Error", f"Error en exportación: {str(e)}")

    def open_document(self):
        try:
            self.app_logic.open_document()
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"No se pudo abrir el documento: {e}")
    
    def capture_from_camera(self):
        """Captura imagen desde la cámara"""
        try:
            dialog = CameraDialog(self)
            if dialog.exec() == 1:
                self.app_logic.set_image_path("output/camera_capture.png")
                self.show_image_preview()
                self.enable_extract_button()
        except ImportError:
            QMessageBox.warning(self, "Dependencia",
                               "Se requiere instalar opencv-python: pip install opencv-python")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error con la cámara: {e}")
    
    def paste_image_from_clipboard(self):
        """Carga imagen desde el portapapeles"""
        try:
            image_path = ClipboardManager.save_clipboard_image("clipboard_image.png")
            if image_path:
                self.app_logic.set_image_path(image_path)
                self.show_image_preview()
                self.enable_extract_button()
            else:
                QMessageBox.warning(self, "Advertencia", 
                                   "No hay imagen en el portapapeles")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al pegar: {e}")
    
    def edit_text(self):
        """Abre el editor de texto"""
        if self.extracted_text:
            text_str = '\n'.join(self.extracted_text)
            dialog = TextEditorDialog(text_str, self)
            if dialog.exec() == 1:
                edited = dialog.get_edited_text()
                self.extracted_text = edited.split('\n')
                QMessageBox.information(self, "Éxito", 
                                      "Texto editado. Guarda para aplicar cambios")
        else:
            QMessageBox.warning(self, "Advertencia",
                               "Primero debes extraer texto de una imagen")
    
    def copy_to_clipboard(self):
        """Copia el texto extraído al portapapeles"""
        if self.extracted_text:
            text = '\n'.join(self.extracted_text)
            if ClipboardManager.copy_text(text):
                QMessageBox.information(self, "Éxito",
                                      f"Texto copiado al portapapeles ({len(text)} caracteres)")
            else:
                QMessageBox.warning(self, "Error", "No se pudo copiar al portapapeles")
        else:
            QMessageBox.warning(self, "Advertencia",
                               "Primero debes extraer texto de una imagen")
    
    def process_batch(self):
        """Abre el diálogo de procesamiento por lotes"""
        dialog = BatchProcessDialog(self.app_logic, self)
        dialog.exec()
    
    def show_statistics(self):
        """Muestra estadísticas y configuración"""
        dialog = StatisticsDialog(self.config_manager, self)
        dialog.exec()
    
    def open_image_tools(self):
        """Abre las herramientas de edición de imagen"""
        if self.app_logic.image_path:
            try:
                dialog = ImageToolsDialog(self.app_logic.image_path, self)
                if dialog.exec() == 1:
                    # Recargar la imagen después de editarla
                    self.show_image_preview()
                    QMessageBox.information(self, "Éxito", "Cambios aplicados a la imagen")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al editar imagen: {e}")
        else:
            QMessageBox.warning(self, "Advertencia", 
                               "Primero debes cargar una imagen")
    
    def open_search_dialog(self):
        """Abre el diálogo de búsqueda"""
        if self.extracted_text:
            text = '\n'.join(self.extracted_text)
            dialog = SearchTextDialog(text, self)
            dialog.exec()
        else:
            QMessageBox.warning(self, "Advertencia",
                               "Primero debes extraer texto de una imagen")
    
    def clear_image(self):
        """Limpia la imagen cargada"""
        self.image_preview.clear()
        self.instruction_label.show()
        self.extract_button.setEnabled(False)
        self.tools_button.setEnabled(False)
        self.search_button.setEnabled(False)
        self.edit_button.setEnabled(False)
        self.copy_button.setEnabled(False)
        self.open_button.setEnabled(False)
        self.extracted_text = None
        self.app_logic.image_path = None
        QMessageBox.information(self, "Limpiado", "Imagen y datos limpiados")
    
    def load_recent_files(self):
        """Carga los archivos recientes (para uso futuro en menú)"""
        self.recent_files = self.config_manager.get_recent_files()
    
    def setup_menu(self):
        """Configura la barra de menús"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        
        open_action = file_menu.addAction("Abrir imagen...")
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.load_image)
        
        file_menu.addSeparator()
        
        camera_action = file_menu.addAction("Capturar desde cámara...")
        camera_action.triggered.connect(self.capture_from_camera)
        
        paste_action = file_menu.addAction("Pegar desde portapapeles")
        paste_action.triggered.connect(self.paste_image_from_clipboard)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Salir")
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        
        # Menú Edición
        edit_menu = menubar.addMenu("Edición")
        
        edit_action = edit_menu.addAction("Editar texto...")
        edit_action.triggered.connect(self.edit_text)
        
        copy_action = edit_menu.addAction("Copiar al portapapeles")
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_to_clipboard)
        
        # Menú Procesar
        process_menu = menubar.addMenu("Procesar")
        
        extract_action = process_menu.addAction("Extraer texto...")
        extract_action.setShortcut(QKeySequence.StandardKey.Save)
        extract_action.triggered.connect(self.extract_text_from_image)
        
        batch_action = process_menu.addAction("Procesamiento por lotes...")
        batch_action.triggered.connect(self.process_batch)
        
        process_menu.addSeparator()
        
        open_doc_action = process_menu.addAction("Abrir documento guardado")
        open_doc_action.triggered.connect(self.open_document)
        
        # Menú Ver
        view_menu = menubar.addMenu("Ver")
        
        stats_action = view_menu.addAction("Estadísticas y configuración...")
        stats_action.triggered.connect(self.show_statistics)
    
    def setup_shortcuts(self):
        """Configura atajos de teclado adicionales"""
        # Los atajos principales se configuran en el menú automáticamente
        # Aquí agregamos los que no están en el menú
        from PyQt6.QtGui import QShortcut
        
        # Ctrl+F para búsqueda
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(self.open_search_dialog)
        
        # Ctrl+L para limpiar
        clear_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        clear_shortcut.activated.connect(self.clear_image)

    def closeEvent(self, event):
        # Limpieza al cerrar la aplicación
        if os.path.exists("temp.png"):
            try:
                os.remove("temp.png")
            except:
                pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Centrar la ventana en la pantalla
    screen = app.primaryScreen().geometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    window.move(x, y)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
