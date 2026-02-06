"""
Ejemplo de uso del sistema con Arquitectura Limpia y Seguridad OWASP
Demuestra cómo integrar todas las capas correctamente
"""

# ============================================================================
# EJEMPLO 1: Extracción OCR Simple con Validación de Seguridad
# ============================================================================

def ejemplo_extraccion_ocr():
    """Extrae texto de una imagen con validación de seguridad"""
    from src.service_container import get_service_container
    from src.infrastructure.security import SecurityLogger
    
    try:
        # Obtener contenedor de servicios
        container = get_service_container()
        
        # Obtener caso de uso
        extract_usecase = container.get('extract_text_usecase')
        
        # Ejecutar extracción (automáticamente valida la imagen)
        result = extract_usecase.execute('/ruta/a/imagen.jpg')
        
        print(f"✅ Extracción exitosa")
        print(f"Texto: {result.text[:100]}...")
        print(f"Confianza: {result.confidence}")
        
    except ValueError as e:
        print(f"❌ Error de validación: {e}")
        SecurityLogger.log_invalid_input('extraction', str(e))


# ============================================================================
# EJEMPLO 2: Exportar Texto a Múltiples Formatos
# ============================================================================

def ejemplo_exportar_texto():
    """Exporta texto extraído a diferentes formatos"""
    from src.service_container import get_service_container
    from src.application.export_usecase import ExportFormat
    from src.infrastructure.security import SecurityLogger
    
    try:
        container = get_service_container()
        export_usecase = container.get('export_text_usecase')
        
        texto_extraido = "Este es el texto extraído de la imagen"
        
        # Exportar a DOCX
        success = export_usecase.execute(
            text=texto_extraido,
            file_path="/ruta/destino.docx",
            format=ExportFormat.DOCX
        )
        
        if success:
            print(f"✅ Exportación a DOCX exitosa")
        else:
            print(f"❌ Error en exportación")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        SecurityLogger.log_invalid_input('export', str(e))


# ============================================================================
# EJEMPLO 3: Procesamiento de Imagen con Seguridad
# ============================================================================

def ejemplo_procesar_imagen():
    """Procesa imagen (rotar, ajustar brillo, etc) con validación"""
    from src.service_container import get_service_container
    from src.domain.entities import Image
    from src.infrastructure.security import SecurityValidator
    
    try:
        # Validar ruta de imagen primero
        image_path = "/ruta/a/imagen.jpg"
        is_valid, error = SecurityValidator.validate_image_path(image_path)
        
        if not is_valid:
            raise ValueError(f"Imagen inválida: {error}")
        
        # Crear entidad de dominio
        image = Image(
            path=image_path,
            width=1920,
            height=1080,
            format="JPEG"
        )
        
        # Obtener container
        container = get_service_container()
        
        # Rotar imagen
        rotate_usecase = container.get('rotate_image_usecase')
        rotated_image = rotate_usecase.execute(image, degrees=90)
        
        print(f"✅ Imagen rotada")
        print(f"Nuevas dimensiones: {rotated_image.width}x{rotated_image.height}")
        
    except ValueError as e:
        print(f"❌ Error: {e}")


# ============================================================================
# EJEMPLO 4: Operación Completa: OCR → Edición → Exportación
# ============================================================================

def ejemplo_flujo_completo():
    """Flujo completo: Cargar imagen → Extraer OCR → Exportar"""
    from src.service_container import get_service_container
    from src.application.export_usecase import ExportFormat
    from src.infrastructure.security import SecurityValidator, SecurityLogger
    
    try:
        # Paso 1: Validar imagen
        image_path = "/ruta/a/documento.jpg"
        is_valid, error = SecurityValidator.validate_image_path(image_path)
        
        if not is_valid:
            raise ValueError(f"Imagen no válida: {error}")
        
        print(f"1️⃣ Imagen validada")
        
        # Paso 2: Extraer texto
        container = get_service_container()
        extract_usecase = container.get('extract_text_usecase')
        
        result = extract_usecase.execute(image_path)
        print(f"2️⃣ OCR completado: {len(result.text)} caracteres")
        
        # Paso 3: Validar texto
        is_valid, error = SecurityValidator.validate_text_input(result.text)
        if not is_valid:
            raise ValueError(f"Texto no válido: {error}")
        
        print(f"3️⃣ Texto validado")
        
        # Paso 4: Exportar a DOCX
        export_usecase = container.get('export_text_usecase')
        
        success = export_usecase.execute(
            text=result.text,
            file_path="/ruta/destino.docx",
            format=ExportFormat.DOCX
        )
        
        print(f"4️⃣ Exportación completada" if success else "4️⃣ Error en exportación")
        
        # Paso 5: Registrar en auditoría
        SecurityLogger.log_event(
            "COMPLETE_FLOW",
            f"OCR + Export successful: {len(result.text)} caracteres",
            "INFO"
        )
        
        print(f"\n✅ Flujo completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en flujo: {e}")
        SecurityLogger.log_security_incident("FLOW_ERROR", str(e))


# ============================================================================
# EJEMPLO 5: Gestión de Configuración Segura
# ============================================================================

def ejemplo_configuracion():
    """Gestiona configuración de aplicación de forma segura"""
    from src.service_container import get_service_container
    from src.domain.entities import Configuration
    
    try:
        container = get_service_container()
        
        # Obtener configuración actual
        get_config = container.get('get_config_usecase')
        current_config = get_config.execute()
        
        print(f"Configuración actual:")
        print(f"  Tema: {current_config.theme}")
        print(f"  GPU: {current_config.use_gpu}")
        
        # Actualizar tema
        update_theme = container.get('update_theme_usecase')
        update_theme.execute('dark')
        
        print(f"✅ Tema actualizado a 'dark'")
        
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")


# ============================================================================
# EJEMPLO 6: Logging de Seguridad y Auditoría
# ============================================================================

def ejemplo_auditoría():
    """Demuestra el logging de seguridad y auditoría"""
    from src.infrastructure.security import SecurityLogger
    from pathlib import Path
    
    # Registrar eventos de seguridad
    SecurityLogger.log_extraction('/ruta/imagen.jpg', True, 2450)
    SecurityLogger.log_export('/ruta/documento.docx', 'DOCX', True)
    SecurityLogger.log_invalid_input('filename', 'Extensión no permitida')
    SecurityLogger.log_security_incident('UNAUTHORIZED_ACCESS', 'Intento de acceso a directorio prohibido')
    
    # Ver archivo de auditoría
    if Path('security.log').exists():
        print("📋 Archivo de auditoría (security.log):")
        print("-" * 60)
        with open('security.log', 'r') as f:
            print(f.read())
    else:
        print("⚠️ Archivo de auditoría no creado aún")


# ============================================================================
# EJEMPLO 7: Manejo Seguro de Errores
# ============================================================================

def ejemplo_errores_seguros():
    """Demuestra manejo seguro de errores sin exponer información interna"""
    from src.infrastructure.security import SecurityValidator, SecurityLogger
    
    # Intentar cargar archivo inválido
    is_valid, error = SecurityValidator.validate_image_path('/admin/secret/imagen.jpg')
    
    if not is_valid:
        # ✅ Error seguro - no expone rutas internas
        print(f"Error seguro: {error}")
        SecurityLogger.log_invalid_input('image_load', error)
    
    # Intentar exportar con caracteres peligrosos
    filename = "documento<script>.txt"
    safe_filename = SecurityValidator.sanitize_filename(filename)
    print(f"Nombre sanitizado: {safe_filename}")
    
    # Intentar cargar archivo muy grande
    is_valid, error = SecurityValidator.validate_image_path('/tmp/huge_file.jpg')
    
    if not is_valid:
        print(f"Error capturado: {error}")


# ============================================================================
# EJEMPLO 8: Validación Multicapa
# ============================================================================

def ejemplo_validacion_multicapa():
    """Demuestra validación en múltiples capas"""
    from src.infrastructure.security import (
        SecurityValidator,
        SecurityLogger,
        SecureFileHandler
    )
    
    # Capa 1: Validación de ruta
    image_path = "/ruta/a/imagen.jpg"
    is_valid, error = SecurityValidator.validate_image_path(image_path)
    
    if not is_valid:
        print(f"❌ Capa 1 - Ruta rechazada: {error}")
        return
    
    print(f"✅ Capa 1 - Ruta validada")
    
    # Capa 2: Lectura segura
    content = SecureFileHandler.safe_read_file(image_path)
    
    if content is None:
        print(f"❌ Capa 2 - Lectura fallida")
        return
    
    print(f"✅ Capa 2 - Archivo leído ({len(content)} bytes)")
    
    # Capa 3: Validación de contenido
    # (Aquí iría validación específica del contenido)
    
    print(f"✅ Todas las capas de validación completadas")


# ============================================================================
# MAIN - Ejecutar ejemplos
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("EJEMPLOS DE USO - ARQUITECTURA LIMPIA + SEGURIDAD OWASP")
    print("=" * 70)
    
    print("\n📌 Ejemplo 1: Extracción OCR")
    print("-" * 70)
    # ejemplo_extraccion_ocr()
    print("(Comentado) Requiere una imagen válida")
    
    print("\n📌 Ejemplo 2: Exportar Texto")
    print("-" * 70)
    # ejemplo_exportar_texto()
    print("(Comentado) Requiere ruta válida")
    
    print("\n📌 Ejemplo 3: Procesar Imagen")
    print("-" * 70)
    # ejemplo_procesar_imagen()
    print("(Comentado) Requiere una imagen válida")
    
    print("\n📌 Ejemplo 4: Flujo Completo")
    print("-" * 70)
    # ejemplo_flujo_completo()
    print("(Comentado) Requiere una imagen válida")
    
    print("\n📌 Ejemplo 5: Gestión de Configuración")
    print("-" * 70)
    # ejemplo_configuracion()
    print("(Comentado) Se ejecutaría cargando configuración")
    
    print("\n📌 Ejemplo 6: Auditoría y Logging")
    print("-" * 70)
    ejemplo_auditoría()
    
    print("\n📌 Ejemplo 7: Manejo Seguro de Errores")
    print("-" * 70)
    ejemplo_errores_seguros()
    
    print("\n📌 Ejemplo 8: Validación Multicapa")
    print("-" * 70)
    # ejemplo_validacion_multicapa()
    print("(Comentado) Requiere archivo válido")
    
    print("\n" + "=" * 70)
    print("✅ Ejemplos completados")
    print("=" * 70)
