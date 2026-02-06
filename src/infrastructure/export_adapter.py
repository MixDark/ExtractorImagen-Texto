"""
Adaptador de exportación - Implementación de exportación a múltiples formatos
"""
from pathlib import Path
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ..domain.repositories import ExportRepository


class MultiFormatExporter(ExportRepository):
    """Implementación de exportador a múltiples formatos"""
    
    def export_to_txt(self, text: str, file_path: str) -> bool:
        """
        Exporta texto a formato TXT
        
        Args:
            text: Texto a exportar
            file_path: Ruta destino
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            print(f"Error exportando TXT: {e}")
            return False
    
    def export_to_docx(self, text: str, file_path: str) -> bool:
        """
        Exporta texto a formato DOCX (Word)
        
        Args:
            text: Texto a exportar
            file_path: Ruta destino
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        try:
            doc = Document()
            
            # Agregar párrafos
            for paragraph_text in text.split('\n'):
                if paragraph_text.strip():
                    doc.add_paragraph(paragraph_text)
            
            doc.save(file_path)
            return True
        except Exception as e:
            print(f"Error exportando DOCX: {e}")
            return False
    
    def export_to_pdf(self, text: str, file_path: str) -> bool:
        """
        Exporta texto a formato PDF
        
        Args:
            text: Texto a exportar
            file_path: Ruta destino
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        try:
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            
            # Configurar fuente
            c.setFont("Helvetica", 11)
            
            # Agregar texto
            y = height - 40
            for line in text.split('\n'):
                if y < 40:
                    c.showPage()
                    y = height - 40
                
                c.drawString(40, y, line[:100])  # Limitar línea
                y -= 15
            
            c.save()
            return True
        except Exception as e:
            print(f"Error exportando PDF: {e}")
            return False
    
    def export_to_rtf(self, text: str, file_path: str) -> bool:
        """
        Exporta texto a formato RTF (Rich Text Format)
        
        Args:
            text: Texto a exportar
            file_path: Ruta destino
            
        Returns:
            True si fue exitoso, False en caso contrario
        """
        try:
            rtf_content = self._generate_rtf(text)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(rtf_content)
            return True
        except Exception as e:
            print(f"Error exportando RTF: {e}")
            return False
    
    @staticmethod
    def _generate_rtf(text: str) -> str:
        """Genera contenido RTF desde texto plano"""
        # Escapar caracteres especiales
        text = text.replace('\\', '\\\\')
        text = text.replace('{', '\\{')
        text = text.replace('}', '\\}')
        text = text.replace('\n', '\\par\\n')
        
        rtf = '{\\rtf1\\ansi\\ansicpg1252\\cocoartf1\n'
        rtf += '{\\colortbl;\\red255\\green255\\blue255;}\n'
        rtf += '{\\*\\expandedcolortbl;;}\n'
        rtf += '\\margl1440\\margr1440\\margtsxn1440\\margbsxn1440\n'
        rtf += '\\f0\\fs20\\cf0\n'
        rtf += text + '\\par\n'
        rtf += '}'
        return rtf
