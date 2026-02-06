"""
Casos de uso para extracción de texto OCR
"""
from typing import Optional
from ..domain.entities import ExtractionResult, Image
from ..domain.repositories import TextExtractionRepository


class ExtractTextUseCase:
    """Usa caso para extraer texto de una imagen"""
    
    def __init__(self, extraction_repository: TextExtractionRepository):
        self.extraction_repository = extraction_repository
    
    def execute(self, image_path: str) -> ExtractionResult:
        """
        Ejecuta la extracción de texto
        
        Args:
            image_path: Ruta de la imagen
            
        Returns:
            ExtractionResult con texto extraído
        """
        # Cargar información de la imagen
        image = self._load_image_info(image_path)
        
        # Extraer texto usando el repositorio
        result = self.extraction_repository.extract_text(image)
        result.image_path = image_path
        
        return result
    
    def _load_image_info(self, image_path: str) -> Image:
        """Carga información básica de la imagen"""
        from PIL import Image as PILImage
        
        img = PILImage.open(image_path)
        width, height = img.size
        
        return Image(
            path=image_path,
            width=width,
            height=height,
            format=img.format or "unknown"
        )


class ExtractBatchUseCase:
    """Caso de uso para extraer texto de múltiples imágenes"""
    
    def __init__(self, extraction_repository: TextExtractionRepository):
        self.extraction_repository = extraction_repository
    
    def execute(self, image_paths: list[str]) -> list[ExtractionResult]:
        """
        Ejecuta la extracción en lote
        
        Args:
            image_paths: Lista de rutas de imágenes
            
        Returns:
            Lista de ExtractionResult
        """
        extract_use_case = ExtractTextUseCase(self.extraction_repository)
        results = []
        
        for path in image_paths:
            try:
                result = extract_use_case.execute(path)
                results.append(result)
            except Exception as e:
                print(f"Error extrayendo {path}: {e}")
        
        return results
