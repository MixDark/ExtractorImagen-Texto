# CHANGELOG

Todas las claves cambios en este proyecto serán documentadas en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto sigue [Semantic Versioning](https://semver.org/lang/es/).

---

## [2.0.0] - 2026-02-05

### ✨ Agregado
- **Arquitectura Limpia**: Reorganización completa en 4 capas (Domain, Application, Infrastructure, Presentation)
- **Inyección de Dependencias**: Sistema centralizado `ServiceContainer` para gestión de dependencias
- **Seguridad OWASP Top 10**: Implementación completa de medidas de seguridad
  - Validación multilayer de entrada
  - Prevención de path traversal
  - Sanitización de nombres de archivo
  - Logging de auditoría completo
  - Manejo seguro de excepciones
- **Múltiples formatos de exportación**: DOCX, PDF, TXT, RTF
- **Captura desde cámara**: Integración con OpenCV para captura directa
- **Procesamiento batch**: Procesar múltiples imágenes en una sola operación
- **Historial de extracciones**: Seguimiento completo de operaciones realizadas
- **Búsqueda y reemplazo**: Herramientas avanzadas de edición de texto
- **Herramientas de imagen**: Rotación, ajuste de brillo y contraste
- **Estadísticas de extracción**: Análisis detallado de operaciones realizadas
- **Temas visual**: Soporte para tema claro y oscuro
- **Documentación completa**: 
  - CLEAN_ARCHITECTURE.md
  - OWASP_SECURITY.md
  - SECURITY_CHECKLIST.md
  - EJEMPLOS_USO.py

### 🔧 Modificado
- Refactorización completa del código base
- Mejora del rendimiento en procesamiento de imágenes
- Optimización de gestión de memoria en operaciones batch
- Interfaz gráfica rediseñada con PyQt6 6.8.0

### 🐛 Corregido
- Manejo mejorado de excepciones en OCR
- Estabilidad en procesamiento de imágenes grandes
- Resolución de problemas con escalado en diferentes resoluciones de pantalla
- Correcciones en exportación de PDF

### 🔒 Seguridad
- Validación de todas las entradas de usuario
- Prevención de inyección de código
- Protección contra acceso a rutas no autorizadas
- Encriptación de datos sensibles donde corresponda

### 📦 Dependencias
- Python 3.13+
- PyQt6 6.8.0
- EasyOCR 1.7.2
- Pillow 11.1.0
- python-docx 1.0.0
- reportlab 4.0.9
- opencv-python 4.8.0.76

---

## [1.0.0] - 2025-01-15

### ✨ Agregado
- Funcionalidad básica de OCR con EasyOCR
- Extracción de texto desde imágenes estáticas
- Soporte para idiomas inglés y español
- Interfaz gráfica básica con PyQt6
- Exportación a archivos de texto
- Configuración mediante archivo JSON

### 🎯 Características principales (v1.0)
- ✅ Reconocimiento de caracteres (OCR)
- ✅ Interfaz gráfica simple
- ✅ Exportación a TXT
- ✅ Configuración básica

---

## [1.5.0] - 2025-06-10

### ✨ Agregado
- Procesamiento batch de múltiples imágenes
- Nuevo formato de exportación: PDF
- Herramientas básicas de edición de imagen
- Sistema de preferencias de usuario
- Historial de archivos recientes

### 🔧 Modificado
- Mejora de la interfaz de usuario
- Optimización del motor OCR
- Actualización a PyQt6 6.5.0

### 🐛 Corregido
- Corrección de problemas de codificación Unicode
- Resolución de errores con ciertos formatos de imagen

---

## [1.8.0] - 2025-10-20

### ✨ Agregado
- Captura desde cámara web
- Editor de texto integrado
- Función de búsqueda y reemplazo
- Temas visuals (claro y oscuro)
- Estadísticas de extracción

### 🔧 Modificado
- Actualización a EasyOCR 1.7.0
- Mejora en rendimiento de búsqueda
- Rediseño de interfaz de usuario

### 🐛 Corregido
- Estabilidad mejorada en procesamiento de imágenes grandes
- Corrección de leaks de memoria
- Resolución de problemas con ciertos codecs de video

---

## [2.0.0-alpha] - 2025-11-01

### ✨ Agregado
- Arquitectura preliminar en capas
- Sistema básico de inyección de dependencias
- Implementación inicial de seguridad

### 🐛 Corregido
- Preparación para lanzamiento major version

---

## [2.0.0-beta] - 2026-01-10

### ✨ Agregado
- Implementación completa de OWASP Top 10
- Documentación de arquitectura limpia
- Sistema completo de logging de auditoría
- Validación multilayer completa

### 🔧 Modificado
- Refinamiento de arquitectura limpia
- Optimización de servicios de seguridad
- Mejora de documentación

### 🐛 Corregido
- Resolución de problemas de seguridad identificados durante beta testing
- Corrección de edge cases en validación

---

## Cómo reportar cambios

Para reportar bugs, pedir nuevas características o sugerir mejoras:

1. Abre un **Issue** en [GitHub](https://github.com)
2. Usa la plantilla de issue disponible
3. Proporciona el máximo detalle posible

---

## Compatibilidad

| Versión | Estado | Soporte |
|---------|--------|---------|
| 2.0.0   | ✅ Actual | Activo |
| 1.8.0   | ⚠️ Legacy | Soporte limitado |
| 1.5.0   | ❌ EOL | No soportado |
| 1.0.0   | ❌ EOL | No soportado |

---

## Licencia

Este proyecto está bajo licencia MIT. Ver LICENSE para más detalles.

---

**Última actualización:** 5 de febrero de 2026
