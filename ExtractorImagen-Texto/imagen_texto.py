import easyocr
from docx import Document
from tkinter import filedialog
import subprocess

class TextExtractorApp:
    def __init__(self):
        self.reader = None
        self.image_path = None
        self.save_path = None

    def set_image_path(self, path):
        self.image_path = path

    def extract_text(self):
        if not self.image_path:
            raise ValueError("Primero debes cargar una imagen.")
        
        if not self.reader:
            self.reader = easyocr.Reader(['en', 'es'])
        
        result = self.reader.readtext(self.image_path, detail=0, paragraph=True)
        if not result:
            raise ValueError("No se detectó texto en la imagen cargada.")
        return result

    def save_text_to_docx(self, text):
        doc = Document()
        for paragraph in text:
            doc.add_paragraph(paragraph)
        
        self.save_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Documento Word", "*.docx")])
        if self.save_path:
            doc.save(self.save_path)
            return self.save_path
        return None

    def open_document(self):
        if self.save_path:
            subprocess.run(["start", self.save_path], check=True, shell=True)