"""
Entidades del dominio para OCR
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from pathlib import Path


@dataclass
class ExtractionResult:
    """Resultado de una extracción de texto OCR"""
    text: str
    confidence: float
    image_path: Optional[str] = None
    timestamp: datetime = None
    language: str = "English"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Image:
    """Representa una imagen para procesamiento"""
    path: str
    width: int
    height: int
    format: str
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 0


@dataclass
class Configuration:
    """Configuración de la aplicación"""
    theme: str = "light"  # light/dark
    language: str = "English"
    ocr_detail_level: int = 0
    use_gpu: bool = False
    paragraph_mode: bool = True


@dataclass
class BatchJobTask:
    """Una tarea dentro de un trabajo en lote"""
    image_path: str
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[ExtractionResult] = None
    error: Optional[str] = None


@dataclass
class BatchJob:
    """Trabajo en lote para procesar múltiples imágenes"""
    job_id: str
    tasks: list[BatchJobTask]
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def total_tasks(self) -> int:
        return len(self.tasks)
    
    @property
    def completed_tasks(self) -> int:
        return sum(1 for t in self.tasks if t.status == "completed")
    
    @property
    def progress(self) -> float:
        if self.total_tasks == 0:
            return 0
        return (self.completed_tasks / self.total_tasks) * 100
