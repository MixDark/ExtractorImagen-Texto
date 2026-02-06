import easyocr
from docx import Document
from PyQt6.QtWidgets import QFileDialog
import subprocess
import os
import platform
import time
import warnings
import logging

# Importar validadores de seguridad
from utils import SecurityValidator, SecurityLogger

# Suprimir warnings de torch
logging.getLogger('torch').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=UserWarning)

class TextExtractorApp:
    def __init__(self):
        self.reader = None
        self.image_path = None
        self.save_path = None

    def set_image_path(self, path):
        """Establece la ruta de la imagen a procesar"""
        # Validar ruta de imagen (OWASP A01)
        is_valid, error = SecurityValidator.validate_image_path(path)
        if not is_valid:
            SecurityLogger.log_invalid_input('image_path', error)
            raise ValueError(f"Ruta de imagen inválida: {error}")
        
        self.image_path = path

    def extract_text(self):
        """Extrae el texto de la imagen usando EasyOCR"""
        if not self.image_path:
            raise ValueError("Primero debes cargar una imagen.")
        
        if not self.reader:
            # Inicializar el lector solo cuando sea necesario para mejorar el rendimiento
            try:
                self.reader = easyocr.Reader(['en', 'es'], gpu=False)
            except Exception as e:
                raise Exception(f"Error al inicializar EasyOCR: {str(e)}")
        
        try:
            # Usar paragraph=True para agrupar el texto en párrafos (más simple)
            result = self.reader.readtext(self.image_path, detail=0, paragraph=True)
            
            if not result or not isinstance(result, list):
                text_list = [""]
            else:
                # Asegurar que todos los elementos son strings
                text_list = []
                for item in result:
                    if item:  # No agregar items vacíos
                        text_list.append(str(item))
            
            if not text_list:
                text_list = [""]
            
            # Validar tamaño del texto extraído (OWASP A03)
            full_text = '\n'.join(text_list)
            is_valid, error = SecurityValidator.validate_text_input(full_text)
            if not is_valid:
                SecurityLogger.log_invalid_input('extracted_text', error)
                raise ValueError(f"Texto extraído inválido: {error}")
            
            # Registrar extracción exitosa (OWASP A09)
            SecurityLogger.log_extraction(self.image_path, True, len(full_text))
            
            return text_list
        except Exception as e:
            # Registrar error de extracción (OWASP A09)
            SecurityLogger.log_extraction(self.image_path, False, 0)
            raise Exception(f"Error al procesar la imagen: {str(e)}")

    def save_text_to_docx(self, text, parent_widget=None):
        """Guarda el texto extraído en un archivo Word"""
        try:
            # Validar texto antes de exportar (OWASP A03)
            full_text = '\n'.join(text) if isinstance(text, list) else str(text)
            is_valid, error = SecurityValidator.validate_text_input(full_text)
            if not is_valid:
                SecurityLogger.log_invalid_input('export_text', error)
                raise ValueError(f"Texto no válido para exportar: {error}")
            
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
                
                # Validar ruta de exportación (OWASP A01, A05)
                is_valid, error = SecurityValidator.validate_export_path(self.save_path, '.docx')
                if not is_valid:
                    SecurityLogger.log_invalid_input('export_path', error)
                    raise ValueError(f"Ruta de exportación inválida: {error}")
                
                doc.save(self.save_path)
                
                # Registrar exportación exitosa (OWASP A09)
                SecurityLogger.log_export(self.save_path, 'DOCX', True)
                return self.save_path
            return None
        except Exception as e:
            # Registrar error de exportación (OWASP A09)
            SecurityLogger.log_export(self.save_path or 'unknown', 'DOCX', False)
            raise Exception(f"Error al guardar el documento: {str(e)}")
    
    def save_text_to_txt(self, text, file_path=None):
        """Guarda el texto extraído en un archivo TXT"""
        try:
            # Validar texto antes de exportar (OWASP A03)
            full_text = '\n'.join(text) if isinstance(text, list) else str(text)
            is_valid, error = SecurityValidator.validate_text_input(full_text)
            if not is_valid:
                SecurityLogger.log_invalid_input('export_text', error)
                raise ValueError(f"Texto no válido para exportar: {error}")
            
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    caption="Guardar como TXT",
                    directory=os.path.expanduser("~/Documents"),
                    filter="Archivo de texto (*.txt)"
                )
            
            if file_path:
                if not file_path.lower().endswith('.txt'):
                    file_path += '.txt'
                
                # Validar ruta de exportación (OWASP A01, A05)
                is_valid, error = SecurityValidator.validate_export_path(file_path, '.txt')
                if not is_valid:
                    SecurityLogger.log_invalid_input('export_path', error)
                    raise ValueError(f"Ruta de exportación inválida: {error}")
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(text))
                self.save_path = file_path
                
                # Registrar exportación exitosa (OWASP A09)
                SecurityLogger.log_export(file_path, 'TXT', True)
                return file_path
            return None
        except Exception as e:
            # Registrar error de exportación (OWASP A09)
            SecurityLogger.log_export(file_path or 'unknown', 'TXT', False)
            raise Exception(f"Error al guardar TXT: {str(e)}")
    
    def save_text_to_pdf(self, text, file_path=None):
        """Guarda el texto extraído en un archivo PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Validar texto antes de exportar (OWASP A03)
            full_text = '\n'.join(text) if isinstance(text, list) else str(text)
            is_valid, error = SecurityValidator.validate_text_input(full_text)
            if not is_valid:
                SecurityLogger.log_invalid_input('export_text', error)
                raise ValueError(f"Texto no válido para exportar: {error}")
            
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    caption="Guardar como PDF",
                    directory=os.path.expanduser("~/Documents"),
                    filter="Archivo PDF (*.pdf)"
                )
            
            if file_path:
                if not file_path.lower().endswith('.pdf'):
                    file_path += '.pdf'
                
                # Validar ruta de exportación (OWASP A01, A05)
                is_valid, error = SecurityValidator.validate_export_path(file_path, '.pdf')
                if not is_valid:
                    SecurityLogger.log_invalid_input('export_path', error)
                    raise ValueError(f"Ruta de exportación inválida: {error}")
                
                doc = SimpleDocTemplate(file_path, pagesize=A4,
                                       rightMargin=72, leftMargin=72,
                                       topMargin=72, bottomMargin=18)
                
                styles = getSampleStyleSheet()
                story = []
                
                for paragraph_text in text:
                    story.append(Paragraph(paragraph_text, styles['BodyText']))
                    story.append(Spacer(1, 0.2*inch))
                
                doc.build(story)
                self.save_path = file_path
                
                # Registrar exportación exitosa (OWASP A09)
                SecurityLogger.log_export(file_path, 'PDF', True)
                return file_path
            return None
        except ImportError:
            raise Exception("Se requiere instalar 'reportlab' para exportar a PDF")
        except Exception as e:
            # Registrar error de exportación (OWASP A09)
            SecurityLogger.log_export(file_path or 'unknown', 'PDF', False)
            raise Exception(f"Error al guardar PDF: {str(e)}")
    
    def save_text_to_rtf(self, text, file_path=None):
        """Guarda el texto extraído en un archivo RTF"""
        try:
            # Validar texto antes de exportar (OWASP A03)
            full_text = '\n'.join(text) if isinstance(text, list) else str(text)
            is_valid, error = SecurityValidator.validate_text_input(full_text)
            if not is_valid:
                SecurityLogger.log_invalid_input('export_text', error)
                raise ValueError(f"Texto no válido para exportar: {error}")
            
            if not file_path:
                file_path, _ = QFileDialog.getSaveFileName(
                    caption="Guardar como RTF",
                    directory=os.path.expanduser("~/Documents"),
                    filter="Archivo RTF (*.rtf)"
                )
            
            if file_path:
                if not file_path.lower().endswith('.rtf'):
                    file_path += '.rtf'
                
                # Validar ruta de exportación (OWASP A01, A05)
                is_valid, error = SecurityValidator.validate_export_path(file_path, '.rtf')
                if not is_valid:
                    SecurityLogger.log_invalid_input('export_path', error)
                    raise ValueError(f"Ruta de exportación inválida: {error}")
                
                rtf_content = "{\\rtf1\\ansi\\ansicpg1252\\cocoartf2\n"
                rtf_content += "{\\fonttbl\\f0\\fswiss Helvetica;}\n"
                rtf_content += "{\\colortbl;\\red255\\green255\\blue255;}\n"
                rtf_content += "\\viewkind4\\uc1\\pard\\f0\\fs20 "
                
                for paragraph in text:
                    # Escapar caracteres especiales (OWASP A03)
                    clean_text = paragraph.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')
                    rtf_content += clean_text + "\\par "
                
                rtf_content += "}"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(rtf_content)
                self.save_path = file_path
                
                # Registrar exportación exitosa (OWASP A09)
                SecurityLogger.log_export(file_path, 'RTF', True)
                return file_path
            return None
        except Exception as e:
            # Registrar error de exportación (OWASP A09)
            SecurityLogger.log_export(file_path or 'unknown', 'RTF', False)
            raise Exception(f"Error al guardar RTF: {str(e)}")
    
    def export_to_format(self, text, format_type, file_path=None):
        """
        Exporta el texto a diferentes formatos
        format_type: 'docx', 'txt', 'pdf', 'rtf'
        """
        if format_type.lower() == 'docx':
            return self.save_text_to_docx(text)
        elif format_type.lower() == 'txt':
            return self.save_text_to_txt(text, file_path)
        elif format_type.lower() == 'pdf':
            return self.save_text_to_pdf(text, file_path)
        elif format_type.lower() == 'rtf':
            return self.save_text_to_rtf(text, file_path)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")

    def open_document(self):
        """Abre el documento guardado con la aplicación predeterminada del sistema"""
        if not self.save_path:
            raise ValueError("No hay ningún documento para abrir.")
        
        if not os.path.exists(self.save_path):
            raise FileNotFoundError("El archivo no existe en la ubicación especificada.")

        try:
            # Validar ruta antes de abrir (OWASP A01)
            is_valid, error = SecurityValidator.validate_export_path(self.save_path, '')
            if not is_valid:
                SecurityLogger.log_invalid_input('open_document_invalid', error)
                raise ValueError(f"Ruta de documento inválida: {error}")
            
            system = platform.system().lower()
            
            if system == 'windows':
                os.startfile(self.save_path)
            elif system == 'darwin':  # macOS
                subprocess.run(['open', self.save_path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', self.save_path], check=True)
        except Exception as e:
            SecurityLogger.log_invalid_input('open_document_error', str(e))
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
