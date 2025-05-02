# =============================================
# HEADER INFORMATION
# =============================================
# Nombre del archivo: view/patients.py
# Propósito: Interfaz gráfica para la gestión de pacientes
# Empresa: DiamondNetSolutions
# Autor: [Nombre del Autor]
# Fecha de creación: [Fecha de Creación]
# Última modificación: [Fecha de Modificación]
# =============================================


import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import datetime
import sys
import json

# Añadir la ruta raíz del proyecto al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.patient_manager import PatientManager
from utils.image_utils import resize_image, save_image


class PatientsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.patient_manager = PatientManager()
        self.selected_patient_id = None
        self.photo_path = None
        self.thumbnail = None

        # Crear widgets
        self.create_widgets()

        # Cargar datos
        self.load_patients()

    def create_widgets(self):
        # Frame con dos secciones: lista de pacientes y detalles de paciente
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame izquierdo para la lista de pacientes
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Barra de búsqueda
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Buscar paciente:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_patients())
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Lista de pacientes
        self.patient_tree = ttk.Treeview(left_frame, columns=("id", "nombre", "apellidos", "telefono"), show="headings")
        self.patient_tree.heading("id", text="ID")
        self.patient_tree.heading("nombre", text="Nombre")
        self.patient_tree.heading("apellidos", text="Apellidos")
        self.patient_tree.heading("telefono", text="Teléfono")

        self.patient_tree.column("id", width=50)
        self.patient_tree.column("nombre", width=150)
        self.patient_tree.column("apellidos", width=150)
        self.patient_tree.column("telefono", width=100)

        self.patient_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.patient_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.patient_tree.configure(yscrollcommand=scrollbar.set)

        # Botones de acción para la lista
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(button_frame, text="Nuevo Paciente", command=self.new_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar Paciente", command=self.edit_patient).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar Paciente", command=self.delete_patient).pack(side=tk.LEFT, padx=5)

        # Vincular evento de selección
        self.patient_tree.bind("<<TreeviewSelect>>", self.on_patient_select)

        # Frame derecho para los detalles del paciente
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Detalles del paciente
        details_frame = ttk.LabelFrame(right_frame, text="Detalles del Paciente")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Foto del paciente
        photo_frame = ttk.Frame(details_frame)
        photo_frame.pack(fill=tk.X, padx=5, pady=5)

        self.photo_label = ttk.Label(photo_frame)
        self.photo_label.pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(photo_frame, text="Cargar Foto", command=self.load_photo).pack(side=tk.LEFT, padx=5)

        # Formulario de datos
        form_frame = ttk.Frame(details_frame)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Primera fila
        row1 = ttk.Frame(form_frame)
        row1.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row1, text="Nombre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.nombre_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.nombre_var).grid(row=0, column=1, sticky=tk.W + tk.E, padx=5, pady=5)

        ttk.Label(row1, text="Apellidos:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.apellidos_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.apellidos_var).grid(row=0, column=3, sticky=tk.W + tk.E, padx=5, pady=5)

        # Segunda fila
        row2 = ttk.Frame(form_frame)
        row2.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row2, text="Fecha de Nacimiento:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.fecha_nacimiento_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.fecha_nacimiento_var).grid(row=0, column=1, sticky=tk.W + tk.E, padx=5,
                                                                     pady=5)
        ttk.Label(row2, text="(DD/MM/AAAA)").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

        # Tercera fila
        row3 = ttk.Frame(form_frame)
        row3.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row3, text="Teléfono:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.telefono_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.telefono_var).grid(row=0, column=1, sticky=tk.W + tk.E, padx=5, pady=5)

        ttk.Label(row3, text="Email:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(row3, textvariable=self.email_var).grid(row=0, column=3, sticky=tk.W + tk.E, padx=5, pady=5)

        # Cuarta fila
        row4 = ttk.Frame(form_frame)
        row4.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(row4, text="Dirección:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.direccion_var = tk.StringVar()
        ttk.Entry(row4, textvariable=self.direccion_var).grid(row=0, column=1, columnspan=3, sticky=tk.W + tk.E, padx=5,
                                                              pady=5)

        # Quinta fila - Notas
        row5 = ttk.Frame(form_frame)
        row5.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Label(row5, text="Notas médicas:").pack(anchor=tk.W, padx=5, pady=5)
        self.notas_text = tk.Text(row5, height=5)
        self.notas_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botones de acción para el formulario
        action_frame = ttk.Frame(details_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)

        self.save_button = ttk.Button(action_frame, text="Guardar", command=self.save_patient)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(action_frame, text="Cancelar", command=self.clear_form)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # Inicialmente deshabilitar botones de guardar y cancelar
        self.save_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)

    def load_patients(self):
        # Limpiar treeview
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)

        # Obtener pacientes de la base de datos
        patients = self.patient_manager.get_all_patients()

        # Insertar pacientes en el treeview
        for patient in patients:
            self.patient_tree.insert("", tk.END, values=(patient['id'], patient['nombre'], patient['apellidos'],
                                                         patient['telefono']))

    def search_patients(self):
        # Obtener texto de búsqueda
        search_text = self.search_var.get().lower()

        # Limpiar treeview
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)

        # Obtener pacientes de la base de datos
        patients = self.patient_manager.search_patients(search_text)

        # Insertar pacientes en el treeview
        for patient in patients:
            self.patient_tree.insert("", tk.END, values=(patient['id'], patient['nombre'], patient['apellidos'],
                                                         patient['telefono']))

    def on_patient_select(self, event):
        # Obtener ID del paciente seleccionado
        selection = self.patient_tree.selection()
        if not selection:
            return

        item = self.patient_tree.item(selection[0])
        self.selected_patient_id = item['values'][0]

        # Cargar datos del paciente
        patient = self.patient_manager.get_patient_by_id(self.selected_patient_id)
        if patient:
            # Llenar formulario
            self.nombre_var.set(patient['nombre'])
            self.apellidos_var.set(patient['apellidos'])
            self.fecha_nacimiento_var.set(patient['fecha_nacimiento'])
            self.telefono_var.set(patient['telefono'])
            self.email_var.set(patient['email'])
            self.direccion_var.set(patient['direccion'])
            self.notas_text.delete("1.0", tk.END)
            if patient['notas_medicas']:
                self.notas_text.insert(tk.END, patient['notas_medicas'])

            # Cargar foto si existe
            self.load_patient_photo(patient['foto_path'])

            # Habilitar botones
            self.save_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.NORMAL)

    def load_patient_photo(self, photo_path):
        # Resetear foto actual
        self.photo_path = None
        self.photo_label.config(image="")

        if photo_path and os.path.exists(photo_path):
            try:
                # Cargar y redimensionar imagen
                self.photo_path = photo_path
                image = Image.open(photo_path)
                self.thumbnail = resize_image(image, (150, 150))
                self.photo_label.config(image=self.thumbnail)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")

    def load_photo(self):
        # Abrir diálogo para seleccionar archivo
        filepath = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=(("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos los archivos", "*.*"))
        )

        if filepath:
            try:
                # Cargar y redimensionar imagen
                self.photo_path = filepath
                image = Image.open(filepath)
                self.thumbnail = resize_image(image, (150, 150))
                self.photo_label.config(image=self.thumbnail)
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")

    def new_patient(self):
        # Limpiar formulario
        self.clear_form()

        # Limpiar selección
        for selected_item in self.patient_tree.selection():
            self.patient_tree.selection_remove(selected_item)

        # Resetear ID seleccionado
        self.selected_patient_id = None

        # Habilitar botones
        self.save_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.NORMAL)

    def edit_patient(self):
        # Verificar que haya un paciente seleccionado
        if not self.selected_patient_id:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un paciente primero.")
            return

    def delete_patient(self):
        # Verificar que haya un paciente seleccionado
        if not self.selected_patient_id:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un paciente primero.")
            return

        # Confirmar eliminación
        if messagebox.askyesno("Confirmar Eliminación",
                               "¿Está seguro de que desea eliminar este paciente? Esta acción no se puede deshacer."):
            try:
                # Eliminar paciente
                self.patient_manager.delete_patient(self.selected_patient_id)

                # Actualizar lista
                self.load_patients()

                # Limpiar formulario
                self.clear_form()

                messagebox.showinfo("Éxito", "Paciente eliminado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar paciente: {str(e)}")

    def save_patient(self):
        # Obtener datos del formulario
        nombre = self.nombre_var.get()
        apellidos = self.apellidos_var.get()
        fecha_nacimiento = self.fecha_nacimiento_var.get()
        telefono = self.telefono_var.get()
        email = self.email_var.get()
        direccion = self.direccion_var.get()
        notas_medicas = self.notas_text.get("1.0", tk.END).strip()

        # Validar datos obligatorios
        if not nombre or not apellidos:
            messagebox.showwarning("Datos incompletos",
                                   "Por favor, complete al menos el nombre y apellidos del paciente.")
            return

        # Validar formato de fecha
        if fecha_nacimiento:
            try:
                dia, mes, anio = fecha_nacimiento.split('/')
                datetime.datetime(int(anio), int(mes), int(dia))
            except:
                messagebox.showwarning("Formato incorrecto", "La fecha de nacimiento debe tener el formato DD/MM/AAAA.")
                return

        try:
            # Preparar datos del paciente
            patient_data = {
                'nombre': nombre,
                'apellidos': apellidos,
                'fecha_nacimiento': fecha_nacimiento,
                'telefono': telefono,
                'email': email,
                'direccion': direccion,
                'notas_medicas': notas_medicas,
                'foto_path': None
            }

            # Guardar foto si existe
            if self.photo_path:
                # Crear carpeta de fotos si no existe
                photos_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'photos'))
                os.makedirs(photos_dir, exist_ok=True)

                # Generar nombre de archivo único
                filename = f"{nombre}_{apellidos}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                new_path = os.path.join(photos_dir, filename)

                # Guardar imagen
                if self.photo_path != new_path:
                    save_image(self.photo_path, new_path)
                    patient_data['foto_path'] = new_path

            # Guardar o actualizar paciente
            if self.selected_patient_id:
                patient_data['id'] = self.selected_patient_id
                self.patient_manager.update_patient(patient_data)
                messagebox.showinfo("Éxito", "Paciente actualizado correctamente.")
            else:
                new_id = self.patient_manager.add_patient(patient_data)
                self.selected_patient_id = new_id
                messagebox.showinfo("Éxito", "Paciente agregado correctamente.")

            # Actualizar lista
            self.load_patients()

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar paciente: {str(e)}")

    def clear_form(self):
        # Limpiar variables
        self.nombre_var.set("")
        self.apellidos_var.set("")
        self.fecha_nacimiento_var.set("")
        self.telefono_var.set("")
        self.email_var.set("")
        self.direccion_var.set("")
        self.notas_text.delete("1.0", tk.END)

        # Limpiar foto
        self.photo_path = None
        self.photo_label.config(image="")

        # Desactivar botones
        self.save_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    # Para pruebas
    import sqlite3

    root = tk.Tk()
    root.title("Gestión de Pacientes")
    root.geometry("900x600")

    # Conexión a la base de datos
    conn = sqlite3.connect(":memory:")

    # Crear tabla de pacientes para pruebas
    conn.execute('''
                 CREATE TABLE IF NOT EXISTS pacientes
                 (
                     id
                     INTEGER
                     PRIMARY
                     KEY
                     AUTOINCREMENT,
                     nombre
                     TEXT
                     NOT
                     NULL,
                     apellidos
                     TEXT
                     NOT
                     NULL,
                     fecha_nacimiento
                     TEXT,
                     telefono
                     TEXT,
                     email
                     TEXT,
                     direccion
                     TEXT,
                     notas_medicas
                     TEXT,
                     foto_path
                     TEXT
                 )
                 ''')

    # Insertar datos de prueba
    conn.execute('''
                 INSERT INTO pacientes (nombre, apellidos, telefono, email)
                 VALUES ('Juan', 'Pérez', '555-123-4567', 'juan@example.com'),
                        ('María', 'González', '555-987-6543', 'maria@example.com'),
                        ('Carlos', 'Rodríguez', '555-456-7890', 'carlos@example.com')
                 ''')
    conn.commit()

    app = PatientsFrame(root, conn)
    root.mainloop()