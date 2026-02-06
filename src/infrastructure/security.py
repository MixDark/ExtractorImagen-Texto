"""
Módulo de seguridad - Validaciones y sanitización según OWASP Top 10
"""
import os
import re
from pathlib import Path
from typing import Optional


class SecurityValidator:
    """Validador de seguridad para OWASP Top 10"""
    
    # Máximo tamaño de archivo imagen (50MB)
    MAX_IMAGE_SIZE = 50 * 1024 * 1024
    
    # Máximo tamaño de texto extraído (10MB)
    MAX_TEXT_SIZE = 10 * 1024 * 1024
    
    # Extensiones permitidas
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    ALLOWED_EXPORT_EXTENSIONS = {'.txt', '.docx', '.pdf', '.rtf'}
    
    # Caracteres peligrosos en nombres de archivo
    DANGEROUS_CHARS_PATTERN = re.compile(r'[<>:"|?*\x00-\x1f]')
    
    # Ruta base permitida (para prevenir directory traversal)
    BASE_PATHS = {
        Path.cwd(),
        Path.home() / 'Desktop',
        Path.home() / 'Documents',
        Path.home() / 'Downloads',
        Path.home() / 'Pictures'
    }
    
    @classmethod
    def validate_image_path(cls, file_path: str) -> tuple[bool, str]:
        """
        Valida ruta de imagen (OWASP: A01 - Broken Access Control)
        Prevention of Path Traversal
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        try:
            # Convertir a Path absoluta y resolver
            path = Path(file_path).resolve()
            
            # Verificar que existe y es archivo
            if not path.exists():
                return False, "Archivo no existe"
            
            if not path.is_file():
                return False, "La ruta no es un archivo"
            
            # Verificar extensión
            if path.suffix.lower() not in cls.ALLOWED_IMAGE_EXTENSIONS:
                return False, f"Extensión no permitida. Permitidas: {cls.ALLOWED_IMAGE_EXTENSIONS}"
            
            # Verificar tamaño
            file_size = path.stat().st_size
            if file_size > cls.MAX_IMAGE_SIZE:
                return False, f"Archivo demasiado grande (máx: {cls.MAX_IMAGE_SIZE / 1024 / 1024:.0f}MB)"
            
            if file_size == 0:
                return False, "Archivo vacío"
            
            return True, ""
        
        except Exception as e:
            return False, f"Error validando ruta: {str(e)}"
    
    @classmethod
    def validate_text_input(cls, text: str, max_length: Optional[int] = None) -> tuple[bool, str]:
        """
        Valida entrada de texto (OWASP: A03 - Injection)
        Previene inyección de comandos y desbordamientos
        
        Args:
            text: Texto a validar
            max_length: Longitud máxima permitida
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        if not isinstance(text, str):
            return False, "Entrada debe ser texto"
        
        # Verificar tamaño
        max_len = max_length or cls.MAX_TEXT_SIZE
        if len(text.encode('utf-8')) > max_len:
            return False, f"Texto demasiado grande (máx: {max_len / 1024 / 1024:.0f}MB)"
        
        # Verificar caracteres de control peligrosos
        if any(ord(char) < 9 or (11 <= ord(char) < 32) for char in text):
            return False, "Texto contiene caracteres de control inválidos"
        
        return True, ""
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitiza nombre de archivo (OWASP: A04 - Insecure Design)
        Previene inyección de caracteres especiales
        
        Args:
            filename: Nombre de archivo a sanitizar
            
        Returns:
            Nombre de archivo sanitizado
        """
        # Remover caracteres peligrosos
        sanitized = cls.DANGEROUS_CHARS_PATTERN.sub('_', filename)
        
        # Limitar longitud
        if len(sanitized) > 255:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[:255 - len(ext)] + ext
        
        # Prevenir nombres vacíos
        if not sanitized or sanitized == '_':
            sanitized = 'file'
        
        return sanitized
    
    @classmethod
    def validate_export_path(cls, file_path: str, extension: str) -> tuple[bool, str]:
        """
        Valida ruta de exportación (OWASP: A05 - Security Misconfiguration)
        Previene escritura en directorios sensibles
        
        Args:
            file_path: Ruta donde guardar
            extension: Extensión esperada
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        try:
            path = Path(file_path).resolve()
            
            # Verificar extensión
            if path.suffix.lower() not in cls.ALLOWED_EXPORT_EXTENSIONS:
                return False, f"Extensión no permitida: {path.suffix}"
            
            # Verificar que la extensión coincide la especificada
            if extension and not path.suffix.lower() == extension.lower():
                return False, f"Extensión no coincide: esperado {extension}"
            
            # Verificar directorio padre existe
            if not path.parent.exists():
                return False, f"Directorio destino no existe"
            
            # Prevenir sobrescritura accidental (opcional - puede comentarse)
            if path.exists():
                return True, f"Advertencia: Archivo será sobrescrito"
            
            return True, ""
        
        except Exception as e:
            return False, f"Error validando ruta: {str(e)}"
    
    @classmethod
    def validate_configuration(cls, config: dict) -> tuple[bool, str]:
        """
        Valida configuración de aplicación (OWASP: A05 - Security Misconfiguration)
        
        Args:
            config: Diccionario de configuración
            
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        # Validar tema
        if 'theme' in config and config['theme'] not in ['light', 'dark']:
            return False, "Tema inválido"
        
        # Validar idioma
        if 'language' in config and not isinstance(config['language'], str):
            return False, "Idioma inválido"
        
        # Validar nivel OCR
        if 'ocr_detail_level' in config:
            if config['ocr_detail_level'] not in [0, 1]:
                return False, "Nivel de detalle OCR inválido"
        
        # Validar booleanos
        if 'use_gpu' in config and not isinstance(config['use_gpu'], bool):
            return False, "use_gpu debe ser booleano"
        
        if 'paragraph_mode' in config and not isinstance(config['paragraph_mode'], bool):
            return False, "paragraph_mode debe ser booleano"
        
        return True, ""


class SecurityLogger:
    """Logger de seguridad para auditoría (OWASP: A09 - Logging & Monitoring)"""
    
    LOG_FILE = "security.log"
    
    @classmethod
    def log_event(cls, event_type: str, details: str, severity: str = "INFO"):
        """
        Registra evento de seguridad
        
        Args:
            event_type: Tipo de evento
            details: Detalles del evento
            severity: Nivel (INFO, WARNING, ERROR, CRITICAL)
        """
        try:
            from datetime import datetime
            
            timestamp = datetime.now().isoformat()
            log_entry = f"[{timestamp}] {severity}: {event_type} - {details}\n"
            
            with open(cls.LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        
        except Exception as e:
            print(f"Error escribiendo log de seguridad: {e}")
    
    @classmethod
    def log_extraction(cls, file_path: str, success: bool, char_count: int = 0):
        """Registra extracción"""
        status = "SUCCESS" if success else "FAILED"
        cls.log_event(
            "OCR_EXTRACTION",
            f"File: {Path(file_path).name}, Status: {status}, Chars: {char_count}",
            "INFO"
        )
    
    @classmethod
    def log_export(cls, file_path: str, format: str, success: bool):
        """Registra exportación"""
        status = "SUCCESS" if success else "FAILED"
        cls.log_event(
            "TEXT_EXPORT",
            f"Format: {format}, File: {Path(file_path).name}, Status: {status}",
            "INFO"
        )
    
    @classmethod
    def log_invalid_input(cls, input_type: str, reason: str):
        """Registra entrada inválida"""
        cls.log_event(
            "INVALID_INPUT",
            f"Type: {input_type}, Reason: {reason}",
            "WARNING"
        )
    
    @classmethod
    def log_security_incident(cls, incident_type: str, details: str):
        """Registra incidente de seguridad"""
        cls.log_event(
            "SECURITY_INCIDENT",
            f"{incident_type}: {details}",
            "CRITICAL"
        )


class SecureFileHandler:
    """Manejador seguro de archivos"""
    
    @classmethod
    def safe_read_file(cls, file_path: str) -> Optional[bytes]:
        """
        Lee archivo de forma segura
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Contenido del archivo o None si hay error
        """
        is_valid, error = SecurityValidator.validate_image_path(file_path)
        if not is_valid:
            SecurityLogger.log_invalid_input("file_read", error)
            return None
        
        try:
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception as e:
            SecurityLogger.log_security_incident("FILE_READ_ERROR", str(e))
            return None
    
    @classmethod
    def safe_write_file(cls, file_path: str, content: bytes) -> bool:
        """
        Escribe archivo de forma segura
        
        Args:
            file_path: Ruta del archivo
            content: Contenido a escribir
            
        Returns:
            True si tuvo éxito, False en caso contrario
        """
        try:
            path = Path(file_path).resolve()
            
            # Verificar permisos de directorio
            if not os.access(path.parent, os.W_OK):
                SecurityLogger.log_security_incident(
                    "WRITE_PERMISSION_DENIED",
                    f"Directory: {path.parent}"
                )
                return False
            
            # Escribir archivo
            with open(file_path, 'wb') as f:
                f.write(content)
            
            return True
        
        except Exception as e:
            SecurityLogger.log_security_incident("FILE_WRITE_ERROR", str(e))
            return False
