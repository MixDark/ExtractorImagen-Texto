"""
Casos de uso para gestión de configuración
"""
from ..domain.entities import Configuration
from ..domain.repositories import ConfigurationRepository


class GetConfigurationUseCase:
    """Caso de uso para obtener la configuración actual"""
    
    def __init__(self, config_repository: ConfigurationRepository):
        self.config_repository = config_repository
    
    def execute(self) -> Configuration:
        """Obtiene la configuración actual"""
        return self.config_repository.get_configuration()


class SaveConfigurationUseCase:
    """Caso de uso para guardar la configuración"""
    
    def __init__(self, config_repository: ConfigurationRepository):
        self.config_repository = config_repository
    
    def execute(self, config: Configuration) -> None:
        """
        Guarda la configuración
        
        Args:
            config: Objeto Configuration con los valores a guardar
        """
        if not config:
            raise ValueError("Configuración inválida")
        
        if config.theme not in ["light", "dark"]:
            raise ValueError("Tema inválido: debe ser 'light' o 'dark'")
        
        self.config_repository.save_configuration(config)


class UpdateThemeUseCase:
    """Caso de uso para actualizar el tema"""
    
    def __init__(self, config_repository: ConfigurationRepository):
        self.config_repository = config_repository
    
    def execute(self, theme: str) -> None:
        """
        Actualiza el tema de la aplicación
        
        Args:
            theme: 'light' o 'dark'
        """
        if theme not in ["light", "dark"]:
            raise ValueError("Tema inválido: debe ser 'light' o 'dark'")
        
        config = self.config_repository.get_configuration()
        config.theme = theme
        self.config_repository.save_configuration(config)
