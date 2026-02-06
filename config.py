import json
import os
from datetime import datetime
from pathlib import Path

# Importar validadores de seguridad
from utils import SecurityValidator, SecurityLogger

class ConfigManager:
    """Gestor de configuración y historial de la aplicación"""
    
    def __init__(self):
        self.config_file = "config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """Carga la configuración desde el archivo JSON"""
        if os.path.exists(self.config_file):
            try:
                # Validar permisos de archivo (OWASP A01)
                SecurityLogger.log_file_access(self.config_file, 'config_load_attempt')
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                SecurityLogger.log_invalid_input('config_load', str(e))
                return self.get_default_config()
        return self.get_default_config()
    
    def get_default_config(self):
        """Retorna la configuración por defecto"""
        return {
            "theme": "light",
            "default_export_format": "docx",
            "save_directory": str(Path.home() / "Documents"),
            "recent_files": [],
            "statistics": {
                "total_characters": 0,
                "files_processed": 0,
                "total_processing_time": 0
            }
        }
    
    def save_config(self):
        """Guarda la configuración en el archivo JSON"""
        try:
            SecurityLogger.log_file_access(self.config_file, 'config_save_attempt')
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            SecurityLogger.log_invalid_input('config_save', str(e))
    
    def get(self, key, default=None):
        """Obtiene un valor de la configuración"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Establece un valor en la configuración"""
        # Validar entradas (OWASP A03)
        if key == "theme":
            if value not in ["light", "dark"]:
                SecurityLogger.log_invalid_input('config_set_theme', f"Invalid theme: {value}")
                return
        elif key == "default_export_format":
            if value not in ["docx", "txt", "pdf", "rtf"]:
                SecurityLogger.log_invalid_input('config_set_format', f"Invalid format: {value}")
                return
        
        self.config[key] = value
        self.save_config()
    
    def add_to_recent(self, file_path, char_count):
        """Agrega un archivo al historial de recientes"""
        # Validar ruta del archivo (OWASP A01, A05)
        is_valid, error = SecurityValidator.validate_image_path(file_path)
        if not is_valid:
            SecurityLogger.log_invalid_input('add_to_recent_validation', error)
            return
        
        recent = self.config.get("recent_files", [])
        
        # Sanitizar nombre de archivo para el registro
        filename = Path(file_path).name
        
        new_entry = {
            "path": file_path,
            "timestamp": datetime.now().isoformat(),
            "characters": char_count
        }
        
        # Remover duplicados y agregar el nuevo al inicio
        recent = [r for r in recent if r["path"] != file_path]
        recent.insert(0, new_entry)
        
        # Mantener solo los últimos 10 (OWASP A01 - evitar consumo excesivo)
        self.config["recent_files"] = recent[:10]
        self.save_config()
        SecurityLogger.log_file_access(file_path, 'added_to_recent')
    
    def get_recent_files(self):
        """Retorna el historial de archivos recientes"""
        return self.config.get("recent_files", [])
    
    def update_statistics(self, char_count, processing_time):
        """Actualiza las estadísticas de uso"""
        # Validar números (OWASP A03)
        try:
            char_count = int(char_count)
            processing_time = float(processing_time)
            
            if char_count < 0 or processing_time < 0:
                SecurityLogger.log_invalid_input('update_statistics', 'Negative values')
                return
        except (ValueError, TypeError):
            SecurityLogger.log_invalid_input('update_statistics', 'Invalid numeric values')
            return
        
        stats = self.config.get("statistics", {
            "total_characters": 0,
            "files_processed": 0,
            "total_processing_time": 0
        })
        
        stats["total_characters"] += char_count
        stats["files_processed"] += 1
        stats["total_processing_time"] += processing_time
        
        self.config["statistics"] = stats
        self.save_config()
    
    def get_statistics(self):
        """Retorna las estadísticas de uso"""
        return self.config.get("statistics", {})
    
    def clear_recent(self):
        """Limpia el historial de recientes"""
        self.config["recent_files"] = []
        self.save_config()
        SecurityLogger.log_invalid_input('clear_recent', 'Recent files history cleared')
    
    def set_theme(self, theme):
        """Establece el tema (light/dark)"""
        if theme not in ["light", "dark"]:
            SecurityLogger.log_invalid_input('set_theme', f"Invalid theme requested: {theme}")
            return
        self.set("theme", theme)
    
    def get_theme(self):
        """Obtiene el tema actual"""
        return self.get("theme", "light")
