# =============================================
# HEADER INFORMATION
# =============================================
# Nombre del archivo: view/patients.py
# Propósito: Interfaz gráfica a para la gestión de pacientes
# Empresa: DiamondNetSolutions
# Autor: [Nombre del Autor]
# Fecha de creación: [Fecha de Creación]
# Última modificación: [Fecha de Modificación]
# Versión: 2.0
# =============================================

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import datetime
import sys
import json
from typing import Optional, Dict, List

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("light")  # Modo claro, oscuro o system
ctk.set_default_color_theme("blue")  # Temas: blue, green, dark-blue

# Añadir la ruta raíz del proyecto al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.patient_manager import PatientManager
from utils.image_utils import resize_image, save_image


class PatientsFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.patient_manager = PatientManager()
        self.selected_patient_id: Optional[int] = None
        self.photo_path: Optional[str] = None
        self.thumbnail: Optional[ImageTk.PhotoImage] = None

        # Configuración de estilo
        self.font_title = ctk.CTkFont(family="Roboto", size=16, weight="bold")
        self.font_label = ctk.CTkFont(family="Roboto", size=12)
        self.font_input = ctk.CTkFont(family="Roboto", size=12)

        # Crear widgets
        self.create_widgets()

        # Cargar datos
        self.load_patients()

    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        self.pack(fill="both", expand=True, padx=10, pady=10)

        # Frame principal con dos secciones
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Frame izquierdo para la lista de pacientes
        left_frame = ctk.CTkFrame(main_frame, width=300)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)

        # Título de la sección
        ctk.CTkLabel(left_frame, text="Lista de Pacientes", font=self.font_title).pack(pady=10)

        # Barra de búsqueda
        search_frame = ctk.CTkFrame(left_frame)
        search_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Buscar:", font=self.font_label).pack(side="left", padx=5)
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.search_patients())
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, font=self.font_input)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<Return>", lambda e: self.search_patients())

        # Lista de pacientes con estilo o
        self.patient_tree = ttk.Treeview(
            left_frame,
            columns=("id", "nombre", "apellidos", "telefono"),
            show="headings",
            style="mystyle.Treeview"
        )

        # Configurar estilo para el Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "mystyle.Treeview",
            background="#ffffff",
            foreground="black",
            rowheight=30,
            fieldbackground="#ffffff",
            borderwidth=0,
            font=self.font_input
        )
        style.map("mystyle.Treeview", background=[('selected', '#0078d7')])

        self.patient_tree.heading("id", text="ID")
        self.patient_tree.heading("nombre", text="Nombre")
        self.patient_tree.heading("apellidos", text="Apellidos")
        self.patient_tree.heading("telefono", text="Teléfono")

        self.patient_tree.column("id", width=50, anchor="center")
        self.patient_tree.column("nombre", width=120)
        self.patient_tree.column("apellidos", width=120)
        self.patient_tree.column("telefono", width=100, anchor="center")

        self.patient_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Scrollbar para la lista
        scrollbar = ctk.CTkScrollbar(left_frame, orientation="vertical", command=self.patient_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.patient_tree.configure(yscrollcommand=scrollbar.set)

        # Botones de acción para la lista
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            button_frame,
            text="Nuevo Paciente",
            command=self.new_patient,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            button_frame,
            text="Editar",
            command=self.edit_patient,
            fg_color="#2196F3",
            hover_color="#0b7dda"
        ).pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkButton(
            button_frame,
            text="Eliminar",
            command=self.delete_patient,
            fg_color="#f44336",
            hover_color="#d32f2f"
        ).pack(side="left", padx=5, expand=True, fill="x")

        # Vincular evento de selección
        self.patient_tree.bind("<<TreeviewSelect>>", self.on_patient_select)

        # Frame derecho para los detalles del paciente
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Título de la sección
        ctk.CTkLabel(right_frame, text="Detalles del Paciente", font=self.font_title).pack(pady=10)

        # Contenedor con pestañas para organizar la información
        self.tabview = ctk.CTkTabview(right_frame)
        self.tabview.pack(fill="both", expand=True, padx=5, pady=5)

        # Crear pestañas
        self.tabview.add("Datos Personales")
        self.tabview.add("Historial Médico")
        self.tabview.add("Documentos")

        # ========== Pestaña de Datos Personales ==========
        personal_frame = self.tabview.tab("Datos Personales")

        # Foto del paciente y datos básicos
        top_frame = ctk.CTkFrame(personal_frame)
        top_frame.pack(fill="x", padx=5, pady=5)

        # Frame para la foto
        photo_frame = ctk.CTkFrame(top_frame, width=180, height=200)
        photo_frame.pack_propagate(False)
        photo_frame.pack(side="left", padx=10, pady=5)

        self.photo_label = ctk.CTkLabel(photo_frame, text="Foto del Paciente", fg_color="#f0f0f0", corner_radius=8)
        self.photo_label.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkButton(
            photo_frame,
            text="Cargar Foto",
            command=self.load_photo,
            height=30
        ).pack(fill="x", padx=5, pady=(0, 5))

        # Frame para los datos básicos
        basic_data_frame = ctk.CTkFrame(top_frame)
        basic_data_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Formulario de datos personales
        form_frame = ctk.CTkScrollableFrame(personal_frame)
        form_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Datos personales
        ctk.CTkLabel(form_frame, text="Información Personal", font=self.font_title).grid(row=0, column=0, columnspan=2,
                                                                                         pady=10, sticky="w")

        # Nombre y apellidos
        ctk.CTkLabel(form_frame, text="Nombre:", font=self.font_label).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.nombre_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.nombre_var, font=self.font_input).grid(row=1, column=1, sticky="ew",
                                                                                          padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Apellidos:", font=self.font_label).grid(row=2, column=0, sticky="w", padx=5,
                                                                               pady=5)
        self.apellidos_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.apellidos_var, font=self.font_input).grid(row=2, column=1,
                                                                                             sticky="ew", padx=5,
                                                                                             pady=5)

        # Fecha de nacimiento y género
        ctk.CTkLabel(form_frame, text="Fecha Nacimiento:", font=self.font_label).grid(row=3, column=0, sticky="w",
                                                                                      padx=5, pady=5)
        self.fecha_nacimiento_var = ctk.StringVar()
        fecha_entry = ctk.CTkEntry(form_frame, textvariable=self.fecha_nacimiento_var, placeholder_text="DD/MM/AAAA",
                                   font=self.font_input)
        fecha_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Género:", font=self.font_label).grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.genero_var = ctk.StringVar(value="No especificado")
        ctk.CTkOptionMenu(form_frame, variable=self.genero_var,
                          values=["Masculino", "Femenino", "Otro", "No especificado"], font=self.font_input).grid(row=4,
                                                                                                                  column=1,
                                                                                                                  sticky="ew",
                                                                                                                  padx=5,
                                                                                                                  pady=5)

        # Información de contacto
        ctk.CTkLabel(form_frame, text="Información de Contacto", font=self.font_title).grid(row=5, column=0,
                                                                                            columnspan=2, pady=10,
                                                                                            sticky="w")

        ctk.CTkLabel(form_frame, text="Teléfono:", font=self.font_label).grid(row=6, column=0, sticky="w", padx=5,
                                                                              pady=5)
        self.telefono_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.telefono_var, font=self.font_input).grid(row=6, column=1,
                                                                                            sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Email:", font=self.font_label).grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.email_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.email_var, font=self.font_input).grid(row=7, column=1, sticky="ew",
                                                                                         padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Dirección:", font=self.font_label).grid(row=8, column=0, sticky="w", padx=5,
                                                                               pady=5)
        self.direccion_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.direccion_var, font=self.font_input).grid(row=8, column=1,
                                                                                             sticky="ew", padx=5,
                                                                                             pady=5)

        # Información adicional
        ctk.CTkLabel(form_frame, text="Información Adicional", font=self.font_title).grid(row=9, column=0, columnspan=2,
                                                                                          pady=10, sticky="w")

        ctk.CTkLabel(form_frame, text="Seguro Médico:", font=self.font_label).grid(row=10, column=0, sticky="w", padx=5,
                                                                                   pady=5)
        self.seguro_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.seguro_var, font=self.font_input).grid(row=10, column=1, sticky="ew",
                                                                                          padx=5, pady=5)

        ctk.CTkLabel(form_frame, text="Número de Seguro:", font=self.font_label).grid(row=11, column=0, sticky="w",
                                                                                      padx=5, pady=5)
        self.num_seguro_var = ctk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.num_seguro_var, font=self.font_input).grid(row=11, column=1,
                                                                                              sticky="ew", padx=5,
                                                                                              pady=5)

        # Configurar peso de columnas para que los campos se expandan
        form_frame.columnconfigure(1, weight=1)

        # ========== Pestaña de Historial Médico ==========
        medical_frame = self.tabview.tab("Historial Médico")

        # Notas médicas
        ctk.CTkLabel(medical_frame, text="Historial Clínico", font=self.font_title).pack(pady=10, anchor="w")

        self.notas_text = ctk.CTkTextbox(medical_frame, font=self.font_input, wrap="word")
        self.notas_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Botones de acción para el formulario
        action_frame = ctk.CTkFrame(right_frame)
        action_frame.pack(fill="x", padx=5, pady=5)

        self.save_button = ctk.CTkButton(
            action_frame,
            text="Guardar",
            command=self.save_patient,
            fg_color="#4CAF50",
            hover_color="#45a049",
            state="disabled"
        )
        self.save_button.pack(side="left", padx=5, expand=True, fill="x")

        self.cancel_button = ctk.CTkButton(
            action_frame,
            text="Cancelar",
            command=self.clear_form,
            fg_color="#607D8B",
            hover_color="#546E7A",
            state="disabled"
        )
        self.cancel_button.pack(side="left", padx=5, expand=True, fill="x")

        # ========== Pestaña de Documentos ==========
        docs_frame = self.tabview.tab("Documentos")

        # Frame para lista de documentos
        docs_list_frame = ctk.CTkFrame(docs_frame)
        docs_list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Lista de documentos (simulada)
        ctk.CTkLabel(docs_list_frame, text="Documentos Adjuntos", font=self.font_title).pack(pady=5)

        self.docs_tree = ttk.Treeview(
            docs_list_frame,
            columns=("tipo", "fecha", "descripcion"),
            show="headings",
            style="mystyle.Treeview",
            height=8
        )

        self.docs_tree.heading("tipo", text="Tipo")
        self.docs_tree.heading("fecha", text="Fecha")
        self.docs_tree.heading("descripcion", text="Descripción")

        self.docs_tree.column("tipo", width=100)
        self.docs_tree.column("fecha", width=100)
        self.docs_tree.column("descripcion", width=200)

        self.docs_tree.pack(fill="both", expand=True, padx=5, pady=5)

        # Botones para documentos
        docs_button_frame = ctk.CTkFrame(docs_frame)
        docs_button_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(
            docs_button_frame,
            text="Agregar Documento",
            command=self.add_document,
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            docs_button_frame,
            text="Ver Documento",
            command=self.view_document,
            width=120,
            state="disabled"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            docs_button_frame,
            text="Eliminar Documento",
            command=self.delete_document,
            width=120,
            fg_color="#f44336",
            hover_color="#d32f2f",
            state="disabled"
        ).pack(side="left", padx=5)

    def load_patients(self):
        """Carga la lista de pacientes desde la base de datos"""
        # Limpiar treeview
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)

        # Obtener pacientes de la base de datos
        patients = self.patient_manager.get_all_patients()

        # Insertar pacientes en el treeview
        for patient in patients:
            self.patient_tree.insert("", "end", values=(
                patient['id'],
                patient['nombre'],
                patient['apellidos'],
                patient['telefono']
            ))

    def search_patients(self):
        """Busca pacientes según el texto ingresado"""
        search_text = self.search_var.get().lower()

        # Limpiar treeview
        for item in self.patient_tree.get_children():
            self.patient_tree.delete(item)

        # Obtener pacientes de la base de datos
        patients = self.patient_manager.search_patients(search_text)

        # Insertar pacientes en el treeview
        for patient in patients:
            self.patient_tree.insert("", "end", values=(
                patient['id'],
                patient['nombre'],
                patient['apellidos'],
                patient['telefono']
            ))

    def on_patient_select(self, event):
        """Maneja la selección de un paciente en la lista"""
        selection = self.patient_tree.selection()
        if not selection:
            return

        item = self.patient_tree.item(selection[0])
        self.selected_patient_id = item['values'][0]

        # Cargar datos del paciente
        patient = self.patient_manager.get_patient_by_id(self.selected_patient_id)
        if patient:
            # Llenar formulario con datos personales
            self.nombre_var.set(patient.get('nombre', ''))
            self.apellidos_var.set(patient.get('apellidos', ''))
            self.fecha_nacimiento_var.set(patient.get('fecha_nacimiento', ''))
            self.genero_var.set(patient.get('genero', 'No especificado'))
            self.telefono_var.set(patient.get('telefono', ''))
            self.email_var.set(patient.get('email', ''))
            self.direccion_var.set(patient.get('direccion', ''))
            self.seguro_var.set(patient.get('seguro_medico', ''))
            self.num_seguro_var.set(patient.get('numero_seguro', ''))

            # Limpiar y cargar notas médicas
            self.notas_text.delete("1.0", "end")
            if patient.get('notas_medicas'):
                self.notas_text.insert("end", patient['notas_medicas'])

            # Cargar foto si existe
            self.load_patient_photo(patient.get('foto_path'))

            # Habilitar botones
            self.save_button.configure(state="normal")
            self.cancel_button.configure(state="normal")

            # Cargar documentos (simulado)
            self.load_documents(patient.get('id'))

    def load_patient_photo(self, photo_path: Optional[str]):
        """Carga la foto del paciente si existe"""
        # Resetear foto actual
        self.photo_path = None
        self.photo_label.configure(image="")

        if photo_path and os.path.exists(photo_path):
            try:
                # Cargar y redimensionar imagen
                self.photo_path = photo_path
                image = Image.open(photo_path)
                self.thumbnail = resize_image(image, (150, 150))
                photo_img = ctk.CTkImage(light_image=image, size=(150, 150))
                self.photo_label.configure(image=photo_img, text="")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")
                self.photo_label.configure(image=None, text="Foto no disponible")

    def load_photo(self):
        """Permite al usuario cargar una foto para el paciente"""
        filepath = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=(
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Todos los archivos", "*.*")
            )
        )

        if filepath:
            try:
                # Cargar y redimensionar imagen
                self.photo_path = filepath
                image = Image.open(filepath)
                self.thumbnail = resize_image(image, (150, 150))
                photo_img = ctk.CTkImage(light_image=image, size=(150, 150))
                self.photo_label.configure(image=photo_img, text="")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar la imagen: {str(e)}")

    def load_documents(self, patient_id: int):
        """Carga los documentos asociados al paciente (simulado)"""
        # Limpiar lista de documentos
        for item in self.docs_tree.get_children():
            self.docs_tree.delete(item)

        # Simulación de documentos (en una implementación real, esto vendría de la base de datos)
        sample_docs = [
            ("Receta", "01/01/2023", "Receta médica para tratamiento"),
            ("Examen", "15/02/2023", "Resultados de análisis clínicos"),
            ("Informe", "10/03/2023", "Informe de consulta")
        ]

        for doc in sample_docs:
            self.docs_tree.insert("", "end", values=doc)

    def new_patient(self):
        """Prepara el formulario para un nuevo paciente"""
        # Limpiar formulario
        self.clear_form()

        # Limpiar selección
        for selected_item in self.patient_tree.selection():
            self.patient_tree.selection_remove(selected_item)

        # Resetear ID seleccionado
        self.selected_patient_id = None

        # Habilitar botones
        self.save_button.configure(state="normal")
        self.cancel_button.configure(state="normal")

        # Enfocar el primer campo
        self.nombre_var.set("")
        self.after(100, lambda: self.focus_set())

    def edit_patient(self):
        """Edita el paciente seleccionado"""
        if not self.selected_patient_id:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un paciente primero.")
            return

    def delete_patient(self):
        """Elimina el paciente seleccionado"""
        if not self.selected_patient_id:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un paciente primero.")
            return

        # Confirmar eliminación
        if messagebox.askyesno(
                "Confirmar Eliminación",
                "¿Está seguro de que desea eliminar este paciente?\nEsta acción no se puede deshacer."
        ):
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
        """Guarda los datos del paciente (nuevo o existente)"""
        # Validar datos obligatorios
        nombre = self.nombre_var.get().strip()
        apellidos = self.apellidos_var.get().strip()

        if not nombre or not apellidos:
            messagebox.showwarning(
                "Datos incompletos",
                "Por favor, complete al menos el nombre y apellidos del paciente."
            )
            return

        # Validar formato de fecha
        fecha_nacimiento = self.fecha_nacimiento_var.get().strip()
        if fecha_nacimiento:
            try:
                dia, mes, anio = fecha_nacimiento.split('/')
                datetime.datetime(int(anio), int(mes), int(dia))
            except:
                messagebox.showwarning(
                    "Formato incorrecto",
                    "La fecha de nacimiento debe tener el formato DD/MM/AAAA."
                )
                return

        try:
            # Preparar datos del paciente
            patient_data = {
                'nombre': nombre,
                'apellidos': apellidos,
                'fecha_nacimiento': fecha_nacimiento,
                'genero': self.genero_var.get(),
                'telefono': self.telefono_var.get().strip(),
                'email': self.email_var.get().strip(),
                'direccion': self.direccion_var.get().strip(),
                'seguro_medico': self.seguro_var.get().strip(),
                'numero_seguro': self.num_seguro_var.get().strip(),
                'notas_medicas': self.notas_text.get("1.0", "end").strip(),
                'foto_path': None
            }

            # Guardar foto si existe
            if self.photo_path:
                # Crear carpeta de fotos si no existe
                photos_dir = os.path.abspath(os.path.join(
                    os.path.dirname(__file__), '..', 'data', 'photos'))
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
        """Limpia todos los campos del formulario"""
        # Limpiar variables
        self.nombre_var.set("")
        self.apellidos_var.set("")
        self.fecha_nacimiento_var.set("")
        self.genero_var.set("No especificado")
        self.telefono_var.set("")
        self.email_var.set("")
        self.direccion_var.set("")
        self.seguro_var.set("")
        self.num_seguro_var.set("")
        self.notas_text.delete("1.0", "end")

        # Limpiar foto
        self.photo_path = None
        self.photo_label.configure(image=None, text="Foto del Paciente")

        # Limpiar documentos
        for item in self.docs_tree.get_children():
            self.docs_tree.delete(item)

        # Desactivar botones
        self.save_button.configure(state="disabled")
        self.cancel_button.configure(state="disabled")

    def add_document(self):
        """Agrega un nuevo documento al paciente"""
        if not self.selected_patient_id:
            messagebox.showwarning("Advertencia", "Seleccione un paciente primero.")
            return

        # Simulación de agregar documento
        doc_type = "Nuevo Documento"
        doc_date = datetime.datetime.now().strftime("%d/%m/%Y")
        doc_desc = "Descripción del documento"

        self.docs_tree.insert("", "end", values=(doc_type, doc_date, doc_desc))
        messagebox.showinfo("Información", "Funcionalidad de agregar documento simulada.")

    def view_document(self):
        """Visualiza el documento seleccionado"""
        selection = self.docs_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un documento primero.")
            return

        messagebox.showinfo("Información", "Funcionalidad de visualización de documento simulada.")

    def delete_document(self):
        """Elimina el documento seleccionado"""
        selection = self.docs_tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un documento primero.")
            return

        if messagebox.askyesno("Confirmar", "¿Eliminar el documento seleccionado?"):
            self.docs_tree.delete(selection[0])


if __name__ == "__main__":
    # Para pruebas
    import sqlite3

    root = ctk.CTk()
    root.title("Gestión de Pacientes - DiamondNetSolutions")
    root.geometry("1200x700")

    # Conexión a la base de datos
    conn = sqlite3.connect(":memory:")
    conn.commit()
    app = PatientsFrame(root)
    root.mainloop()