from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPixmap
from PIL import Image
import io
import os
import re
from pathlib import Path
from datetime import datetime
import logging

# Configurar logging de seguridad
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

# Crear handler para archivo de log de seguridad
security_handler = logging.FileHandler('security.log')
security_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
security_logger.addHandler(security_handler)


class SecurityValidator:
    """Validador de seguridad para prevenir OWASP Top 10"""
    
    # Límites de seguridad
    MAX_IMAGE_SIZE_MB = 50
    MAX_TEXT_SIZE_MB = 10
    MAX_FILE_PATH_LENGTH = 260
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
    ALLOWED_EXPORT_EXTENSIONS = {'.docx', '.pdf', '.txt', '.rtf'}
    DANGEROUS_PATTERNS = [r'\.\./', r'\.\.\\', r'~/', r'^/etc/', r'^C:\\Windows']
    
    @staticmethod
    def validate_image_path(path):
        """Valida ruta de imagen (OWASP A01, A05)"""
        if not path:
            return False, "Ruta vacía"
        
        if not isinstance(path, str):
            return False, "Ruta debe ser string"
        
        # Limitar longitud de ruta
        if len(path) > SecurityValidator.MAX_FILE_PATH_LENGTH:
            return False, f"Ruta demasiado larga (máx {SecurityValidator.MAX_FILE_PATH_LENGTH})"
        
        # Verificar patrones peligrosos
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, path, re.IGNORECASE):
                return False, f"Ruta contiene patrones peligrosos: {pattern}"
        
        # Verificar extensión permitida
        file_ext = Path(path).suffix.lower()
        if file_ext not in SecurityValidator.ALLOWED_IMAGE_EXTENSIONS:
            return False, f"Extensión no permitida: {file_ext}"
        
        # Verificar que el archivo existe
        if not os.path.exists(path):
            return False, "Archivo no encontrado"
        
        # Verificar tamaño del archivo
        try:
            file_size_mb = os.path.getsize(path) / (1024 * 1024)
            if file_size_mb > SecurityValidator.MAX_IMAGE_SIZE_MB:
                return False, f"Archivo demasiado grande (máx {SecurityValidator.MAX_IMAGE_SIZE_MB}MB)"
        except OSError as e:
            return False, f"Error al leer archivo: {str(e)}"
        
        return True, "OK"
    
    @staticmethod
    def validate_text_input(text):
        """Valida entrada de texto (OWASP A03)"""
        if not isinstance(text, str):
            return False, "Texto debe ser string"
        
        # Limitar tamaño de texto
        text_size_mb = len(text.encode('utf-8')) / (1024 * 1024)
        if text_size_mb > SecurityValidator.MAX_TEXT_SIZE_MB:
            return False, f"Texto demasiado grande (máx {SecurityValidator.MAX_TEXT_SIZE_MB}MB)"
        
        return True, "OK"
    
    @staticmethod
    def validate_export_path(file_path, expected_extension):
        """Valida ruta de exportación (OWASP A01, A05)"""
        if not file_path:
            return False, "Ruta de exportación vacía"
        
        if not isinstance(file_path, str):
            return False, "Ruta debe ser string"
        
        # Limitar longitud
        if len(file_path) > SecurityValidator.MAX_FILE_PATH_LENGTH:
            return False, f"Ruta demasiado larga (máx {SecurityValidator.MAX_FILE_PATH_LENGTH})"
        
        # Verificar patrones peligrosos
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, file_path, re.IGNORECASE):
                return False, f"Ruta contiene patrones peligrosos: {pattern}"
        
        # Verificar extensión
        file_ext = Path(file_path).suffix.lower()
        if expected_extension and file_ext != expected_extension.lower():
            return False, f"Extensión esperada {expected_extension}, obtenido {file_ext}"
        
        if file_ext not in SecurityValidator.ALLOWED_EXPORT_EXTENSIONS:
            return False, f"Extensión no permitida para exportación: {file_ext}"
        
        # Verificar que el directorio existe
        directory = Path(file_path).parent
        if not directory.exists():
            return False, f"Directorio no existe: {directory}"
        
        return True, "OK"
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitiza nombre de archivo (OWASP A03)"""
        # Remover caracteres peligrosos
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\.\.', '', filename)  # Remover ..
        return filename[:200]  # Limitar a 200 caracteres


class SecurityLogger:
    """Sistema de logging de seguridad"""
    
    @staticmethod
    def log_invalid_input(input_type, error):
        """Registra entrada inválida (OWASP A09)"""
        security_logger.warning(f"INVALID_INPUT - Type: {input_type}, Error: {error}")
    
    @staticmethod
    def log_extraction(image_path, success, text_length):
        """Registra intento de extracción (OWASP A09)"""
        status = "SUCCESS" if success else "FAILED"
        filename = Path(image_path).name if image_path else "unknown"
        security_logger.info(f"EXTRACTION - Status: {status}, File: {filename}, TextLength: {text_length}")
    
    @staticmethod
    def log_export(file_path, format_type, success):
        """Registra intento de exportación (OWASP A09)"""
        status = "SUCCESS" if success else "FAILED"
        filename = Path(file_path).name if file_path else "unknown"
        security_logger.info(f"EXPORT - Status: {status}, File: {filename}, Format: {format_type}")
    
    @staticmethod
    def log_file_access(file_path, action):
        """Registra acceso a archivo (OWASP A01)"""
        filename = Path(file_path).name if file_path else "unknown"
        security_logger.info(f"FILE_ACCESS - Action: {action}, File: {filename}")


class ClipboardManager:
    """Gestor del portapapeles"""
    
    @staticmethod
    def copy_text(text):
        """Copia texto al portapapeles"""
        app = QApplication.instance()
        if app:
            clipboard = app.clipboard()
            clipboard.setText(text)
            return True
        return False
    
    @staticmethod
    def get_text_from_clipboard():
        """Obtiene texto del portapapeles"""
        app = QApplication.instance()
        if app:
            clipboard = app.clipboard()
            return clipboard.text()
        return ""
    
    @staticmethod
    def get_image_from_clipboard():
        """Obtiene imagen del portapapeles"""
        app = QApplication.instance()
        if app:
            clipboard = app.clipboard()
            mime_data = clipboard.mimeData()
            
            if mime_data.hasImage():
                image = clipboard.image()
                return image
        return None
    
    @staticmethod
    def save_clipboard_image(file_path):
        """Guarda la imagen del portapapeles a un archivo"""
        image = ClipboardManager.get_image_from_clipboard()
        if image:
            pixmap = QPixmap.fromImage(image)
            pixmap.save(file_path)
            return file_path
        return None


class ImageProcessor:
    """Procesador de imágenes"""
    
    @staticmethod
    def rotate_image(image_path, angle):
        """Rota una imagen"""
        try:
            image = Image.open(image_path)
            rotated = image.rotate(angle, expand=True)
            rotated.save(image_path)
            return True
        except Exception as e:
            print(f"Error al rotar imagen: {e}")
            return False
    
    @staticmethod
    def crop_image(image_path, box):
        """Recorta una imagen (box = (left, top, right, bottom))"""
        try:
            image = Image.open(image_path)
            cropped = image.crop(box)
            cropped.save(image_path)
            return True
        except Exception as e:
            print(f"Error al recortar imagen: {e}")
            return False
    
    @staticmethod
    def adjust_contrast(image_path, factor):
        """Ajusta el contraste de una imagen"""
        try:
            from PIL import ImageEnhance
            image = Image.open(image_path)
            enhancer = ImageEnhance.Contrast(image)
            enhanced = enhancer.enhance(factor)
            enhanced.save(image_path)
            return True
        except Exception as e:
            print(f"Error al ajustar contraste: {e}")
            return False
    
    @staticmethod
    def adjust_brightness(image_path, factor):
        """Ajusta el brillo de una imagen"""
        try:
            from PIL import ImageEnhance
            image = Image.open(image_path)
            enhancer = ImageEnhance.Brightness(image)
            enhanced = enhancer.enhance(factor)
            enhanced.save(image_path)
            return True
        except Exception as e:
            print(f"Error al ajustar brillo: {e}")
            return False
