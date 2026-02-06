"""
Casos de uso para procesamiento de imágenes
"""
from ..domain.entities import Image
from ..domain.repositories import ImageProcessor


class RotateImageUseCase:
    """Caso de uso para rotar una imagen"""
    
    def __init__(self, image_processor: ImageProcessor):
        self.image_processor = image_processor
    
    def execute(self, image: Image, degrees: float) -> Image:
        """Rota una imagen por grados especificados"""
        if not image:
            raise ValueError("Imagen inválida")
        
        return self.image_processor.rotate(image, degrees)


class AdjustBrightnessUseCase:
    """Caso de uso para ajustar brillo"""
    
    def __init__(self, image_processor: ImageProcessor):
        self.image_processor = image_processor
    
    def execute(self, image: Image, factor: float) -> Image:
        """Ajusta el brillo de una imagen"""
        if not image:
            raise ValueError("Imagen inválida")
        
        if factor < 0 or factor > 2:
            raise ValueError("Factor de brillo debe estar entre 0 y 2")
        
        return self.image_processor.adjust_brightness(image, factor)


class AdjustContrastUseCase:
    """Caso de uso para ajustar contraste"""
    
    def __init__(self, image_processor: ImageProcessor):
        self.image_processor = image_processor
    
    def execute(self, image: Image, factor: float) -> Image:
        """Ajusta el contraste de una imagen"""
        if not image:
            raise ValueError("Imagen inválida")
        
        if factor < 0 or factor > 3:
            raise ValueError("Factor de contraste debe estar entre 0 y 3")
        
        return self.image_processor.adjust_contrast(image, factor)


class CropImageUseCase:
    """Caso de uso para recortar una imagen"""
    
    def __init__(self, image_processor: ImageProcessor):
        self.image_processor = image_processor
    
    def execute(self, image: Image, left: int, top: int, right: int, bottom: int) -> Image:
        """Recorta una imagen"""
        if not image:
            raise ValueError("Imagen inválida")
        
        if left < 0 or top < 0 or right > image.width or bottom > image.height:
            raise ValueError("Coordenadas de recorte fuera de límites")
        
        return self.image_processor.crop(image, left, top, right, bottom)
