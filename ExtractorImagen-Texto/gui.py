import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                            QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent, QIcon
from PIL import Image
from imagen_texto import TextExtractorApp

class ExtractionWorker(QThread):
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, app_logic):
        super().__init__()
        self.app_logic = app_logic

    def run(self):
        try:
            self.progress.emit(20)
            result = self.app_logic.extract_text()
            self.progress.emit(100)
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
        self.app_logic = TextExtractorApp()
        self.setup_ui()
        self.apply_styles()
        self.setWindowIcon(QIcon('icon.png'))  

    def setup_ui(self):
        self.setWindowTitle("Extractor de imagen a texto")
        self.setFixedSize(800, 600)

        # Widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

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

        # Contenedor de botones
        button_container = QWidget()
        button_container.setObjectName("buttonContainer")
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(15)

        # Botones animados
        self.load_button = AnimatedButton("Cargar")
        self.save_button = AnimatedButton("Guardar")
        self.open_button = AnimatedButton("Abrir")

        for button in [self.load_button, self.save_button, self.open_button]:
            button_layout.addWidget(button)

        self.save_button.setEnabled(False)
        self.open_button.setEnabled(False)

        # Agregar widgets al layout principal
        main_layout.addWidget(self.image_container)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(button_container)

        # Conectar señales
        self.load_button.clicked.connect(self.load_image)
        self.save_button.clicked.connect(self.save_file)
        self.open_button.clicked.connect(self.open_document)

        # Configurar drag and drop
        self.setAcceptDrops(True)

    def apply_styles(self):
        # Estilo moderno con tema claro
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            
            QWidget {
                color: #333333;
                font-family: 'Segoe UI', Arial, sans-serif;
            }            
            
            #imageContainer {
                background-color: #F5F7FA;
                border-radius: 10px;
                padding: 20px;
                border: 1px solid #E1E5EA;
            }
            
            #imagePreview {
                background-color: #FFFFFF;
                border: 2px dashed #C0C6CC;
                border-radius: 5px;
            }
            
            #imagePreview:hover {
                border-color: #007AFF;
            }
            
            #instructionLabel {
                color: #6B7280;
                font-size: 14px;
                padding: 10px;
            }
            
            #buttonContainer {
                background-color: transparent;
            }
            
            #actionButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
                font-weight: 500;
            }
            
            #actionButton:hover {
                background-color: #0056B3;
            }
            
            #actionButton:disabled {
                background-color: #E1E5EA;
                color: #9CA3AF;
            }
            
            QProgressBar {
                border: none;
                border-radius: 5px;
                text-align: center;
                background-color: #F5F7FA;
                height: 20px;
                color: #333333;
            }
            
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 5px;
            }
            
            QMessageBox {
                background-color: #FFFFFF;
            }
            
            QMessageBox QLabel {
                color: #333333;
            }
            
            QMessageBox QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #0056B3;
            }
        """)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.app_logic.set_image_path(files[0])
            self.show_image_preview()
            self.enable_save_button()

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen",
            "",
            "Imágenes (*.jpg *.jpeg *.png *.bmp *.gif)"
        )
        if file_name:
            self.app_logic.set_image_path(file_name)
            self.show_image_preview()
            self.enable_save_button()

    def show_image_preview(self):
        try:
            image = Image.open(self.app_logic.image_path)
            image.thumbnail((720, 400))
            image.save("temp.png")
            pixmap = QPixmap("temp.png")
            self.image_preview.setPixmap(pixmap)
            self.instruction_label.hide()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar la imagen: {e}")

    def enable_save_button(self):
        self.save_button.setEnabled(True)

    def save_file(self):
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.save_button.setEnabled(False)
        
        self.worker = ExtractionWorker(self.app_logic)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.handle_extraction_finished)
        self.worker.error.connect(self.handle_extraction_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def handle_extraction_finished(self, result):
        try:
            save_path = self.app_logic.save_text_to_docx(result, self)
            if save_path:
                self.progress_bar.setValue(100)
                QMessageBox.information(self, "Guardado", 
                                      f"Texto extraído guardado en: {save_path}")
                self.open_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.save_button.setEnabled(True)
            self.progress_bar.hide()

    def handle_extraction_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.save_button.setEnabled(True)
        self.progress_bar.hide()

    def open_document(self):
        try:
            self.app_logic.open_document()
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                               f"No se pudo abrir el documento: {e}")

    def closeEvent(self, event):
        # Limpieza al cerrar la aplicación
        if os.path.exists("temp.png"):
            try:
                os.remove("temp.png")
            except:
                pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Centrar la ventana en la pantalla
    screen = app.primaryScreen().geometry()
    x = (screen.width() - window.width()) // 2
    y = (screen.height() - window.height()) // 2
    window.move(x, y)
    
    window.show()
    sys.exit(app.exec())
