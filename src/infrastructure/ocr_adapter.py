"""
Adaptador OCR - Implementación de extracción de texto con EasyOCR
"""
import easyocr
from typing import Optional
from ..domain.entities import ExtractionResult, Image
from ..domain.repositories import TextExtractionRepository


class EasyOCRAdapter(TextExtractionRepository):
    """Implementación de extracción de texto usando EasyOCR"""
    
    def __init__(self, languages: list[str] = None, gpu: bool = False, detail: int = 0):
        """
        Inicializa el adaptador OCR
        
        Args:
            languages: Lista de idiomas (ej: ['en', 'es'])
            gpu: Si usar GPU para OCR
            detail: Nivel de detalle (0=mínimo, 1=máximo)
        """
        self.languages = languages or ['en', 'es']
        self.gpu = gpu
        self.detail = detail
        self.reader = easyocr.Reader(self.languages, gpu=self.gpu)
    
    def extract_text(self, image: Image) -> ExtractionResult:
        """
        Extrae texto de una imagen individual
        
        Args:
            image: Objeto Image con la información de la imagen
            
        Returns:
            ExtractionResult con el texto y confianza
        """
        try:
            results = self.reader.readtext(
                image.path,
                detail=self.detail,
                paragraph=True
            )
            
            # Combinar todos los textos extraídos
            extracted_text = '\n'.join(results) if isinstance(results, list) else str(results)
            
            return ExtractionResult(
                text=extracted_text,
                confidence=0.95,  # Valor por defecto
                language=self.languages[0] if self.languages else "English"
            )
        except Exception as e:
            raise RuntimeError(f"Error al extraer texto: {str(e)}")
    
    def extract_text_batch(self, images: list[Image]) -> list[ExtractionResult]:
        """
        Extrae texto de múltiples imágenes
        
        Args:
            images: Lista de objetos Image
            
        Returns:
            Lista de ExtractionResult
        """
        results = []
        for image in images:
            try:
                result = self.extract_text(image)
                results.append(result)
            except Exception as e:
                print(f"Error procesando {image.path}: {e}")
        
        return results
