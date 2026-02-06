"""
Casos de uso para exportación de texto
"""
from enum import Enum
from ..domain.repositories import ExportRepository


class ExportFormat(Enum):
    """Formatos de exportación disponibles"""
    TXT = "txt"
    DOCX = "docx"
    PDF = "pdf"
    RTF = "rtf"


class ExportTextUseCase:
    """Caso de uso para exportar texto extraído"""
    
    def __init__(self, export_repository: ExportRepository):
        self.export_repository = export_repository
    
    def execute(self, text: str, file_path: str, format: ExportFormat) -> bool:
        """
        Ejecuta la exportación de texto
        
        Args:
            text: Texto a exportar
            file_path: Ruta destino del archivo
            format: Formato de exportación
            
        Returns:
            True si se exportó exitosamente, False en caso contrario
        """
        if not text or not text.strip():
            raise ValueError("No hay texto para exportar")
        
        if format == ExportFormat.TXT:
            return self.export_repository.export_to_txt(text, file_path)
        elif format == ExportFormat.DOCX:
            return self.export_repository.export_to_docx(text, file_path)
        elif format == ExportFormat.PDF:
            return self.export_repository.export_to_pdf(text, file_path)
        elif format == ExportFormat.RTF:
            return self.export_repository.export_to_rtf(text, file_path)
        else:
            raise ValueError(f"Formato no soportado: {format}")
