"""
Interfaces y repositorios del dominio
"""
from abc import ABC, abstractmethod
from typing import Optional
from .entities import ExtractionResult, Image, Configuration


class TextExtractionRepository(ABC):
    """Interfaz para extracción de texto"""
    
    @abstractmethod
    def extract_text(self, image: Image) -> ExtractionResult:
        """Extrae texto de una imagen"""
        pass
    
    @abstractmethod
    def extract_text_batch(self, images: list[Image]) -> list[ExtractionResult]:
        """Extrae texto de múltiples imágenes"""
        pass


class ConfigurationRepository(ABC):
    """Interfaz para gestión de configuración"""
    
    @abstractmethod
    def get_configuration(self) -> Configuration:
        """Obtiene la configuración actual"""
        pass
    
    @abstractmethod
    def save_configuration(self, config: Configuration) -> None:
        """Guarda la configuración"""
        pass


class ImageProcessor(ABC):
    """Interfaz para procesamiento de imágenes"""
    
    @abstractmethod
    def rotate(self, image: Image, degrees: float) -> Image:
        """Rota la imagen"""
        pass
    
    @abstractmethod
    def adjust_brightness(self, image: Image, factor: float) -> Image:
        """Ajusta el brillo"""
        pass
    
    @abstractmethod
    def adjust_contrast(self, image: Image, factor: float) -> Image:
        """Ajusta el contraste"""
        pass
    
    @abstractmethod
    def crop(self, image: Image, left: int, top: int, right: int, bottom: int) -> Image:
        """Recorta la imagen"""
        pass


class ExportRepository(ABC):
    """Interfaz para exportar textos extraídos"""
    
    @abstractmethod
    def export_to_txt(self, text: str, file_path: str) -> bool:
        """Exporta a TXT"""
        pass
    
    @abstractmethod
    def export_to_docx(self, text: str, file_path: str) -> bool:
        """Exporta a DOCX"""
        pass
    
    @abstractmethod
    def export_to_pdf(self, text: str, file_path: str) -> bool:
        """Exporta a PDF"""
        pass
    
    @abstractmethod
    def export_to_rtf(self, text: str, file_path: str) -> bool:
        """Exporta a RTF"""
        pass
