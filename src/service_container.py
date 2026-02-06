"""
Inyección de dependencias - Contenedor de servicios
Centraliza la creación de instancias de los casos de uso
"""
from .domain.repositories import (
    TextExtractionRepository,
    ConfigurationRepository,
    ImageProcessor,
    ExportRepository
)
from .application.extraction_usecase import ExtractTextUseCase, ExtractBatchUseCase
from .application.export_usecase import ExportTextUseCase
from .application.image_usecase import (
    RotateImageUseCase,
    AdjustBrightnessUseCase,
    AdjustContrastUseCase,
    CropImageUseCase
)
from .application.configuration_usecase import (
    GetConfigurationUseCase,
    SaveConfigurationUseCase,
    UpdateThemeUseCase
)

# Importaciones condicionales con manejo de errores
try:
    from .infrastructure.ocr_adapter import EasyOCRAdapter
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    EasyOCRAdapter = None

try:
    from .infrastructure.configuration_adapter import FileConfigurationAdapter, ExtractionHistoryAdapter
except ImportError:
    FileConfigurationAdapter = None
    ExtractionHistoryAdapter = None

try:
    from .infrastructure.image_processor import PillowImageProcessor
except ImportError:
    PillowImageProcessor = None

try:
    from .infrastructure.export_adapter import MultiFormatExporter
except ImportError:
    MultiFormatExporter = None


class ServiceContainer:
    """Contenedor centralizado de inyección de dependencias"""
    
    def __init__(self):
        """Inicializa el contenedor de servicios"""
        self._instances = {}
        self._register_repositories()
        self._register_usecases()
    
    def _register_repositories(self):
        """Registra las implementaciones de repositorios"""
        # Registrar OCR adapter solo si está disponible
        if EASYOCR_AVAILABLE and EasyOCRAdapter:
            try:
                self._instances['ocr_repository'] = EasyOCRAdapter(
                    languages=['en', 'es'],
                    gpu=False,
                    detail=0
                )
            except Exception as e:
                print(f"Warning: No se pudo inicializar EasyOCRAdapter: {e}")
                self._instances['ocr_repository'] = None
        else:
            print("Warning: EasyOCR no está disponible, OCR deshabilitado")
            self._instances['ocr_repository'] = None
        
        # Registrar otros adapters
        if FileConfigurationAdapter:
            self._instances['config_repository'] = FileConfigurationAdapter('config.json')
        
        if PillowImageProcessor:
            self._instances['image_processor'] = PillowImageProcessor()
        
        if MultiFormatExporter:
            self._instances['export_repository'] = MultiFormatExporter()
        
        if ExtractionHistoryAdapter:
            self._instances['history_adapter'] = ExtractionHistoryAdapter('extraction_history.json')
    
    def _register_usecases(self):
        """Registra los casos de uso"""
        ocr_repo = self._instances.get('ocr_repository')
        export_repo = self._instances.get('export_repository')
        image_proc = self._instances.get('image_processor')
        
        # Casos de extracción (solo si OCR está disponible)
        if ocr_repo:
            self._instances['extract_text_usecase'] = ExtractTextUseCase(ocr_repo)
            self._instances['extract_batch_usecase'] = ExtractBatchUseCase(ocr_repo)
        else:
            print("Warning: Casos de extracción OCR no disponibles")
            self._instances['extract_text_usecase'] = None
            self._instances['extract_batch_usecase'] = None
        
        # Caso de exportación
        if export_repo:
            self._instances['export_text_usecase'] = ExportTextUseCase(export_repo)
        else:
            print("Warning: Caso de exportación no disponible")
            self._instances['export_text_usecase'] = None
        
        # Casos de procesamiento de imagen
        if image_proc:
            self._instances['rotate_image_usecase'] = RotateImageUseCase(image_proc)
            self._instances['adjust_brightness_usecase'] = AdjustBrightnessUseCase(image_proc)
            self._instances['adjust_contrast_usecase'] = AdjustContrastUseCase(image_proc)
            self._instances['crop_image_usecase'] = CropImageUseCase(image_proc)
        else:
            print("Warning: Casos de procesamiento de imagen no disponibles")
            self._instances['rotate_image_usecase'] = None
            self._instances['adjust_brightness_usecase'] = None
            self._instances['adjust_contrast_usecase'] = None
            self._instances['crop_image_usecase'] = None
        
        config_repo = self._instances.get('config_repository')
        
        # Casos de configuración
        if config_repo:
            self._instances['get_config_usecase'] = GetConfigurationUseCase(config_repo)
            self._instances['save_config_usecase'] = SaveConfigurationUseCase(config_repo)
            self._instances['update_theme_usecase'] = UpdateThemeUseCase(config_repo)
        else:
            print("Warning: Casos de configuración no disponibles")
            self._instances['get_config_usecase'] = None
            self._instances['save_config_usecase'] = None
            self._instances['update_theme_usecase'] = None
    
    def get(self, service_name: str):
        """Obtiene una instancia de servicio por nombre"""
        if service_name not in self._instances:
            raise ValueError(f"Servicio no encontrado: {service_name}")
        
        service = self._instances[service_name]
        if service is None:
            raise ValueError(f"Servicio no disponible (dependencias faltantes): {service_name}")
        
        return service
    
    def get_all(self) -> dict:
        """Obtiene todos los servicios registrados"""
        return self._instances.copy()


# Instancia única del contenedor
_container = None


def get_service_container() -> ServiceContainer:
    """Obtiene o crea la instancia única del contenedor"""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container
