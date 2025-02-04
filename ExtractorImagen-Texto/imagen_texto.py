import easyocr
from docx import Document
from PyQt6.QtWidgets import QFileDialog
import subprocess
import os
import platform

class TextExtractorApp:
    def __init__(self):
        self.reader = None
        self.image_path = None
        self.save_path = None

    def set_image_path(self, path):
        """Establece la ruta de la imagen a procesar"""
        self.image_path = path

    def extract_text(self):
        """Extrae el texto de la imagen usando EasyOCR"""
        if not self.image_path:
            raise ValueError("Primero debes cargar una imagen.")
        
        if not self.reader:
            # Inicializar el lector solo cuando sea necesario para mejorar el rendimiento
            try:
                self.reader = easyocr.Reader(['en', 'es'])
            except Exception as e:
                raise Exception(f"Error al inicializar EasyOCR: {str(e)}")
        
        try:
            result = self.reader.readtext(self.image_path, detail=0, paragraph=True)
            if not result:
                raise ValueError("No se detectó texto en la imagen cargada.")
            return result
        except Exception as e:
            raise Exception(f"Error al procesar la imagen: {str(e)}")

    def save_text_to_docx(self, text, parent_widget=None):
        """Guarda el texto extraído en un archivo Word"""
        try:
            doc = Document()
            for paragraph in text:
                doc.add_paragraph(paragraph)
            
            # Diálogo de guardar archivo usando PyQt6
            self.save_path, _ = QFileDialog.getSaveFileName(
                parent=parent_widget,
                caption="Guardar como",
                directory=os.path.expanduser("~/Documents"),
                filter="Documento Word (*.docx)"
            )
            
            if self.save_path:
                # Asegurar que el archivo termine en .docx
                if not self.save_path.lower().endswith('.docx'):
                    self.save_path += '.docx'
                doc.save(self.save_path)
                return self.save_path
            return None
        except Exception as e:
            raise Exception(f"Error al guardar el documento: {str(e)}")

    def open_document(self):
        """Abre el documento guardado con la aplicación predeterminada del sistema"""
        if not self.save_path:
            raise ValueError("No hay ningún documento para abrir.")
        
        if not os.path.exists(self.save_path):
            raise FileNotFoundError("El archivo no existe en la ubicación especificada.")

        try:
            system = platform.system().lower()
            
            if system == 'windows':
                os.startfile(self.save_path)
            elif system == 'darwin':  # macOS
                subprocess.run(['open', self.save_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', self.save_path], check=True)
        except Exception as e:
            raise Exception(f"Error al abrir el documento: {str(e)}")

    def get_supported_image_formats(self):
        """Retorna una lista de formatos de imagen soportados"""
        return [
            "*.jpg", "*.jpeg", "*.png", "*.bmp", "*.gif", "*.tiff"
        ]

    def cleanup(self):
        """Limpia los recursos utilizados por la aplicación"""
        self.reader = None
        self.image_path = None
        self.save_path = None
