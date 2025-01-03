import tkinter as tk
from tkinter import messagebox, filedialog
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
from imagen_texto import TextExtractorApp

class GUI:
    def __init__(self, root):
        self.root = root
        self.app_logic = TextExtractorApp() 
        self.setup_ui()

    def setup_ui(self):
        self.root.title("Extractor de imagen a texto")
        window_width = 600
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
        self.root.resizable(False, False)
        
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_image)
        
        self.container_frame = tk.Frame(self.root)
        self.container_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.image_preview = tk.Label(self.container_frame)
        self.image_preview.pack(pady=10)

        self.label = tk.Label(self.container_frame, text="Arrastra una imagen aquí o haz clic en 'Cargar'", width=50, height=5)
        self.label.pack(pady=10)

        button_frame = tk.Frame(self.container_frame)
        button_frame.pack(pady=5)

        self.load_button = tk.Button(button_frame, text="Cargar", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(button_frame, text="Guardar", command=self.save_file, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.open_button = tk.Button(button_frame, text="Abrir", command=self.open_document, state=tk.DISABLED)
        self.open_button.pack(side=tk.LEFT, padx=5)

    #Permite arrastra y soltar la imagen dentro de la aplicación
    def drop_image(self, event):
        self.app_logic.set_image_path(event.data.strip('{}'))
        if self.app_logic.image_path:
            self.show_image_preview()
            self.enable_save_button()

    def load_image(self):
        image_path = filedialog.askopenfilename(filetypes=[("Imagenes", "*.jpg *.jpeg *.png *.bmp *.gif")])
        self.app_logic.set_image_path(image_path)
        if image_path:
            self.show_image_preview()
            self.enable_save_button()

    #Vista previa de la imgen
    def show_image_preview(self):
        try:
            image = Image.open(self.app_logic.image_path)
            image.thumbnail((500, 430), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.image_preview.config(image=photo, width=500, height=430)
            self.image_preview.image = photo
            self.label.pack_forget()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar la imagen: {e}")
    
    #Habilita el boton cuando la imagen esta cargada
    def enable_save_button(self):
        self.save_button.config(state=tk.NORMAL)

    def save_file(self):
        try:
            result = self.app_logic.extract_text()
            save_path = self.app_logic.save_text_to_docx(result)
            if save_path:
                messagebox.showinfo("Guardado", f"Texto extraído guardado en: {save_path}")
                self.open_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_document(self):
        try:
            self.app_logic.open_document()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el documento: {e}")

if __name__ == "__main__":
    root = TkinterDnD.Tk()
    gui = GUI(root)
    root.mainloop()