#!/usr/bin/env python3
"""
Punto de entrada principal para el AppImage
Extractor de Imagen a Texto
Integración con Clean Architecture y OWASP Security
"""

import sys
import os
import platform
from pathlib import Path

# Agregar el directorio actual al path para importar los módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Configurar variables de entorno para Qt según el SO
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_SCALE_FACTOR'] = '1'

# Solo usar xcb en Linux
if platform.system() == 'Linux':
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Importar seguridad y logging
from utils import SecurityLogger, SecurityValidator

# Registrar inicio de aplicación
SecurityLogger.log_invalid_input('startup', 'Application started')

def setup_application_security():
    """Configura medidas de seguridad de la aplicación"""
    # Validar que los directorios necesarios existen
    required_dirs = [Path('output'), Path('src')]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                SecurityLogger.log_file_access(str(dir_path), 'created')
            except Exception as e:
                SecurityLogger.log_invalid_input('directory_creation', str(e))
    
    # Verificar permisos de archivos de configuración
    config_files = ['config.json', 'extraction_history.json', 'security.log']
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                # Asegurar que los archivos de configuración solo son legibles/escribibles por el usuario
                if platform.system() != 'Windows':
                    os.chmod(config_file, 0o600)
                SecurityLogger.log_file_access(config_file, 'permissions_checked')
            except Exception as e:
                SecurityLogger.log_invalid_input('permission_check', f"{config_file}: {str(e)}")

def initialize_service_container():
    """Inicializa el contenedor de inyección de dependencias"""
    try:
        from src.service_container import get_service_container
        container = get_service_container()
        SecurityLogger.log_invalid_input('service_container', 'Service container initialized successfully')
        return container
    except ImportError as e:
        SecurityLogger.log_invalid_input('service_container', f"Could not initialize clean architecture: {e}")
        return None
    except Exception as e:
        SecurityLogger.log_invalid_input('service_container', f"Error: {e}")
        return None

# Importar y ejecutar la aplicación principal
from gui import main

if __name__ == "__main__":
    # Configurar seguridad
    setup_application_security()
    
    # Intentar inicializar service container para clean architecture
    service_container = initialize_service_container()
    
    # Ejecutar aplicación
    try:
        main()
    except Exception as e:
        SecurityLogger.log_invalid_input('main_execution', f"Application error: {str(e)}")
        sys.exit(1) 