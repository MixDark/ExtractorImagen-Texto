"""
Adaptador de procesamiento de imágenes - Implementación con Pillow
"""
from PIL import Image as PILImage, ImageEnhance
from ..domain.entities import Image
from ..domain.repositories import ImageProcessor


class PillowImageProcessor(ImageProcessor):
    """Implementación de procesamiento de imágenes usando Pillow"""
    
    def rotate(self, image: Image, degrees: float) -> Image:
        """
        Rota la imagen por grados especificados
        
        Args:
            image: Imagen a rotar
            degrees: Grados de rotación
            
        Returns:
            Imagen rotada
        """
        try:
            pil_image = PILImage.open(image.path)
            rotated = pil_image.rotate(degrees, expand=True)
            
            # Guardar imagen rotada temporalmente
            temp_path = f"{image.path}_rotated.png"
            rotated.save(temp_path)
            
            new_width, new_height = rotated.size
            return Image(
                path=temp_path,
                width=new_width,
                height=new_height,
                format=rotated.format or "PNG"
            )
        except Exception as e:
            raise RuntimeError(f"Error al rotar imagen: {e}")
    
    def adjust_brightness(self, image: Image, factor: float) -> Image:
        """
        Ajusta el brillo de la imagen
        
        Args:
            image: Imagen a ajustar
            factor: Factor de brillo (0=negro, 1=original, 2=muy brillante)
            
        Returns:
            Imagen con brillo ajustado
        """
        try:
            pil_image = PILImage.open(image.path)
            enhancer = ImageEnhance.Brightness(pil_image)
            enhanced = enhancer.enhance(factor)
            
            # Guardar imagen ajustada temporalmente
            temp_path = f"{image.path}_brightness.png"
            enhanced.save(temp_path)
            
            return Image(
                path=temp_path,
                width=image.width,
                height=image.height,
                format=enhanced.format or "PNG"
            )
        except Exception as e:
            raise RuntimeError(f"Error al ajustar brillo: {e}")
    
    def adjust_contrast(self, image: Image, factor: float) -> Image:
        """
        Ajusta el contraste de la imagen
        
        Args:
            image: Imagen a ajustar
            factor: Factor de contraste (0=gris, 1=original, 2=muy contrastado)
            
        Returns:
            Imagen con contraste ajustado
        """
        try:
            pil_image = PILImage.open(image.path)
            enhancer = ImageEnhance.Contrast(pil_image)
            enhanced = enhancer.enhance(factor)
            
            # Guardar imagen ajustada temporalmente
            temp_path = f"{image.path}_contrast.png"
            enhanced.save(temp_path)
            
            return Image(
                path=temp_path,
                width=image.width,
                height=image.height,
                format=enhanced.format or "PNG"
            )
        except Exception as e:
            raise RuntimeError(f"Error al ajustar contraste: {e}")
    
    def crop(self, image: Image, left: int, top: int, right: int, bottom: int) -> Image:
        """
        Recorta la imagen
        
        Args:
            image: Imagen a recortar
            left, top, right, bottom: Coordenadas del rectángulo de recorte
            
        Returns:
            Imagen recortada
        """
        try:
            pil_image = PILImage.open(image.path)
            cropped = pil_image.crop((left, top, right, bottom))
            
            # Guardar imagen recortada temporalmente
            temp_path = f"{image.path}_cropped.png"
            cropped.save(temp_path)
            
            new_width, new_height = cropped.size
            return Image(
                path=temp_path,
                width=new_width,
                height=new_height,
                format=cropped.format or "PNG"
            )
        except Exception as e:
            raise RuntimeError(f"Error al recortar imagen: {e}")
