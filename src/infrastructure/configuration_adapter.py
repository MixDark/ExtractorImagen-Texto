"""
Adaptador de configuración - Gestión de configuración persistente
"""
import json
from pathlib import Path
from typing import Optional
from ..domain.entities import Configuration
from ..domain.repositories import ConfigurationRepository


class FileConfigurationAdapter(ConfigurationRepository):
    """Implementación de configuración persistida en archivo JSON"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        Inicializa el adaptador de configuración
        
        Args:
            config_file: Ruta del archivo de configuración
        """
        self.config_file = Path(config_file)
        self.default_config = Configuration()
    
    def get_configuration(self) -> Configuration:
        """Carga la configuración desde archivo"""
        if not self.config_file.exists():
            return self.default_config
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            return Configuration(
                theme=data.get('theme', 'light'),
                language=data.get('language', 'English'),
                ocr_detail_level=data.get('ocr_detail_level', 0),
                use_gpu=data.get('use_gpu', False),
                paragraph_mode=data.get('paragraph_mode', True)
            )
        except Exception as e:
            print(f"Error cargando configuración: {e}")
            return self.default_config
    
    def save_configuration(self, config: Configuration) -> None:
        """Guarda la configuración en archivo"""
        try:
            data = {
                'theme': config.theme,
                'language': config.language,
                'ocr_detail_level': config.ocr_detail_level,
                'use_gpu': config.use_gpu,
                'paragraph_mode': config.paragraph_mode
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración: {e}")


class ExtractionHistoryAdapter:
    """Adaptador para gestionar historial de extracciones"""
    
    def __init__(self, history_file: str = "extraction_history.json"):
        """
        Inicializa el adaptador de historial
        
        Args:
            history_file: Ruta del archivo de historial
        """
        self.history_file = Path(history_file)
    
    def add_to_history(self, extraction_data: dict) -> None:
        """Agrega una extracción al historial"""
        try:
            history = self._load_history()
            history.append(extraction_data)
            self._save_history(history)
        except Exception as e:
            print(f"Error agregando al historial: {e}")
    
    def get_history(self) -> list:
        """Obtiene el historial de extracciones"""
        try:
            return self._load_history()
        except Exception as e:
            print(f"Error cargando historial: {e}")
            return []
    
    def clear_history(self) -> None:
        """Limpia el historial"""
        try:
            self._save_history([])
        except Exception as e:
            print(f"Error limpiando historial: {e}")
    
    def _load_history(self) -> list:
        """Carga el historial del archivo"""
        if not self.history_file.exists():
            return []
        
        with open(self.history_file, 'r') as f:
            return json.load(f)
    
    def _save_history(self, history: list) -> None:
        """Guarda el historial en archivo"""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
