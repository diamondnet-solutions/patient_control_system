# =============================================
# HEADER INFORMATION
# =============================================
# Nombre del archivo: treatments.py
# Propósito: Gestión integral de tratamientos médicos (creación, modificación, asignación)
# Empresa: DiamondNetSolutions
# Autor: Eliazar
# Fecha de creación: 01/05/2025
# Versión: 2.0
# =============================================

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from datetime import datetime
from typing import Optional, Dict, Any, List
import os
import sys

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("light")  # Modo claro, oscuro o system
ctk.set_default_color_theme("blue")  # Temas: blue, green, dark-blue

# Añadir la ruta raíz del proyecto al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.treatment_manager import TreatmentManager
from core.patient_manager import PatientManager
from db.database import DatabaseManager
from utils.image_utils import resize_image, save_image


class TreatmentsFrame(ctk.CTkFrame):
    """Frame principal para la gestión de tratamientos médicos con CustomTkinter"""

    def __init__(self, parent):
        """
        Inicializa el frame de tratamientos

        Args:
            parent: Widget padre contenedor de este frame
        """
        super().__init__(parent)
        self.parent = parent

        # Configuración de estilo
        self.font_title = ctk.CTkFont(family="Roboto", size=16, weight="bold")
        self.font_label = ctk.CTkFont(family="Roboto", size=12)
        self.font_input = ctk.CTkFont(family="Roboto", size=12)

        # Inicializar managers con DatabaseManager
        db_manager = DatabaseManager()
        self.treatment_manager = TreatmentManager(db_manager)
        self.patient_manager = PatientManager(db_manager)

        # Variables de control
        self.current_treatment_id = None
        self.current_patient_id = None
        self.current_assignment_id = None

        # Widgets
        self.treatments_table = None
        self.history_table = None
        self.patient_combo = None
        self.treatment_combo = None
        self.search_entry = None
        self.price_label = None
        self.duration_label = None

        # Configurar interfaz
        self.setup_ui()

        # Cargar datos iniciales
        self.load_treatments()
        self.load_patients_combo()

        self.pack(fill="both", expand=True)

    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Frame principal con pestañas
        self.notebook = ctk.CTkTabview(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear pestañas
        self.notebook.add("Catálogo")
        self.notebook.add("Asignación")
        self.notebook.add("Historial")

        # Configurar cada pestaña
        self.setup_treatments_tab()
        self.setup_assignment_tab()
        self.setup_history_tab()

    def setup_treatments_tab(self):
        """Configura la pestaña de catálogo de tratamientos"""
        tab = self.notebook.tab("Catálogo")

        # Frame para botones de acción
        actions_frame = ctk.CTkFrame(tab)
        actions_frame.pack(fill="x", padx=5, pady=5)

        # Botones de acción con colores semánticos
        ctk.CTkButton(
            actions_frame,
            text="Agregar",
            command=self.add_treatment,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions_frame,
            text="Editar",
            command=self.edit_treatment,
            fg_color="#2196F3",
            hover_color="#0b7dda"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions_frame,
            text="Eliminar",
            command=self.delete_treatment,
            fg_color="#f44336",
            hover_color="#d32f2f"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            actions_frame,
            text="Actualizar",
            command=self.load_treatments
        ).pack(side="left", padx=5)

        # Frame para búsqueda
        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(search_frame, text="Buscar:").pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=200, placeholder_text="Nombre o descripción...")
        self.search_entry.pack(side="left", padx=5)

        ctk.CTkButton(
            search_frame,
            text="Buscar",
            command=self.search_treatments,
            width=80
        ).pack(side="left", padx=5)

        # Tabla de tratamientos
        table_frame = ctk.CTkFrame(tab)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        columns = ("id", "nombre", "descripción", "precio", "duración", "categoría")
        self.treatments_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
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

        # Configurar columnas
        for col in columns:
            self.treatments_table.heading(col, text=col.capitalize())
            self.treatments_table.column(col, width=120, anchor="center")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.treatments_table.yview)
        scrollbar.pack(side="right", fill="y")
        self.treatments_table.configure(yscrollcommand=scrollbar.set)

        self.treatments_table.pack(fill="both", expand=True)
        self.treatments_table.bind("<Double-1>", lambda e: self.edit_treatment())

    def setup_assignment_tab(self):
        """Configura la pestaña de asignación de tratamientos"""
        tab = self.notebook.tab("Asignación")

        # Frame para selección de paciente
        patient_frame = ctk.CTkFrame(tab)
        patient_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(patient_frame, text="Paciente:").pack(side="left", padx=5)
        self.patient_combo = ctk.CTkComboBox(
            patient_frame,
            state="readonly",
            dropdown_font=self.font_input
        )
        self.patient_combo.pack(side="left", padx=5, fill="x", expand=True)
        self.patient_combo.bind("<<ComboboxSelected>>", self.on_patient_selected)

        # Frame para selección de tratamiento
        treatment_frame = ctk.CTkFrame(tab)
        treatment_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(treatment_frame, text="Tratamiento:").pack(side="left", padx=5)
        self.treatment_combo = ctk.CTkComboBox(
            treatment_frame,
            state="readonly",
            dropdown_font=self.font_input
        )
        self.treatment_combo.pack(side="left", padx=5, fill="x", expand=True)
        self.treatment_combo.bind("<<ComboboxSelected>>", self.update_treatment_info)

        # Frame para información del tratamiento
        info_frame = ctk.CTkFrame(tab)
        info_frame.pack(fill="x", padx=10, pady=5)

        # Grid layout para información
        ctk.CTkLabel(info_frame, text="Precio estándar:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.price_label = ctk.CTkLabel(info_frame, text="$0.00", font=self.font_label)
        self.price_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ctk.CTkLabel(info_frame, text="Duración estimada:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.duration_label = ctk.CTkLabel(info_frame, text="0 minutos", font=self.font_label)
        self.duration_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        # Campo para precio personalizado
        ctk.CTkLabel(info_frame, text="Precio personalizado:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.custom_price_entry = ctk.CTkEntry(info_frame, placeholder_text="Opcional", font=self.font_input)
        self.custom_price_entry.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Campo para notas
        ctk.CTkLabel(info_frame, text="Notas:").grid(row=3, column=0, sticky="nw", padx=5, pady=2)
        self.notes_entry = ctk.CTkTextbox(info_frame, height=60, font=self.font_input)
        self.notes_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        # Configurar peso de columnas
        info_frame.columnconfigure(1, weight=1)

        # Botón para asignar tratamiento
        ctk.CTkButton(
            tab,
            text="Asignar Tratamiento",
            command=self.assign_treatment,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(pady=10)

    def setup_history_tab(self):
        """Configura la pestaña de historial de tratamientos"""
        tab = self.notebook.tab("Historial")

        # Frame para filtros
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(filter_frame, text="Paciente:").pack(side="left", padx=5)
        self.history_patient_combo = ctk.CTkComboBox(
            filter_frame,
            state="readonly",
            width=200,
            dropdown_font=self.font_input
        )
        self.history_patient_combo.pack(side="left", padx=5)

        ctk.CTkLabel(filter_frame, text="Fecha desde:").pack(side="left", padx=5)
        self.date_from_entry = ctk.CTkEntry(filter_frame, width=100, placeholder_text="DD/MM/AAAA")
        self.date_from_entry.pack(side="left", padx=5)
        self.date_from_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ctk.CTkLabel(filter_frame, text="Fecha hasta:").pack(side="left", padx=5)
        self.date_to_entry = ctk.CTkEntry(filter_frame, width=100, placeholder_text="DD/MM/AAAA")
        self.date_to_entry.pack(side="left", padx=5)
        self.date_to_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ctk.CTkButton(
            filter_frame,
            text="Filtrar",
            command=self.filter_history,
            width=80
        ).pack(side="left", padx=5)

        # Tabla de historial
        table_frame = ctk.CTkFrame(tab)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("id", "fecha", "paciente", "tratamiento", "precio", "estado")
        self.history_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            style="mystyle.Treeview"
        )

        # Configurar columnas
        for col in columns:
            self.history_table.heading(col, text=col.capitalize())
            self.history_table.column(col, width=120, anchor="center")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.history_table.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_table.configure(yscrollcommand=scrollbar.set)

        self.history_table.pack(fill="both", expand=True)

    # ==================================================================
    # MÉTODOS DE FUNCIONALIDAD (igual que en la versión original)
    # ==================================================================

    def load_treatments(self):
        """Carga los tratamientos desde el manager y los muestra en la tabla"""
        try:
            treatments = self.treatment_manager.get_all_treatments()
            self.treatments_table.delete(*self.treatments_table.get_children())

            # Actualizar también el combobox de tratamientos
            treatment_list = []

            for treatment in treatments:
                self.treatments_table.insert("", "end", values=(
                    treatment['id'],
                    treatment['name'],
                    treatment['description'],
                    f"${treatment['default_price']:.2f}",
                    f"{treatment['duration']} min",
                    treatment.get('category_name', 'Sin categoría')
                ))
                treatment_list.append(f"{treatment['id']} - {treatment['name']}")

            # Actualizar combobox de tratamientos
            self.treatment_combo.configure(values=treatment_list)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los tratamientos: {str(e)}")

    def load_patients_combo(self):
        """Carga la lista de pacientes en los combobox correspondientes"""
        try:
            patients = self.patient_manager.get_all_patients()
            patient_list = [f"{p['id']} - {p['nombre']} {p['apellidos']}" for p in patients]

            self.patient_combo.configure(values=patient_list)
            self.history_patient_combo.configure(values=patient_list)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los pacientes: {str(e)}")

    def on_patient_selected(self, event=None):
        """Manejador de evento cuando se selecciona un paciente"""
        selected = self.patient_combo.get()
        if selected:
            self.current_patient_id = int(selected.split(" - ")[0])

    def add_treatment(self):
        """Muestra diálogo para agregar un nuevo tratamiento"""
        try:
            # Crear ventana de diálogo
            dialog = ctk.CTkToplevel(self)
            dialog.title("Agregar Nuevo Tratamiento")
            dialog.transient(self)  # Hace que la ventana sea modal respecto a la principal
            dialog.grab_set()  # Impide interactuar con otras ventanas

            # Variables de control
            name_var = ctk.StringVar()
            desc_var = ctk.StringVar()
            price_var = ctk.DoubleVar(value=0.0)
            duration_var = ctk.IntVar(value=30)

            # Campos del formulario
            ctk.CTkLabel(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkEntry(dialog, textvariable=name_var, width=300).grid(row=0, column=1, padx=5, pady=5)

            ctk.CTkLabel(dialog, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkEntry(dialog, textvariable=desc_var, width=300).grid(row=1, column=1, padx=5, pady=5)

            ctk.CTkLabel(dialog, text="Precio:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkEntry(dialog, textvariable=price_var, width=100).grid(row=2, column=1, padx=5, pady=5, sticky="w")

            ctk.CTkLabel(dialog, text="Duración (min):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkEntry(dialog, textvariable=duration_var, width=100).grid(row=3, column=1, padx=5, pady=5, sticky="w")

            # Botones
            btn_frame = ctk.CTkFrame(dialog)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

            ctk.CTkButton(
                btn_frame,
                text="Guardar",
                command=lambda: self.save_new_treatment(
                    dialog, name_var.get(), desc_var.get(), price_var.get(), duration_var.get()
                ),
                fg_color="#4CAF50",
                hover_color="#45a049"
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                btn_frame,
                text="Cancelar",
                command=dialog.destroy,
                fg_color="#607D8B",
                hover_color="#546E7A"
            ).pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el diálogo: {str(e)}")

    def save_new_treatment(self, dialog, name, description, price, duration):
        """Guarda un nuevo tratamiento en la base de datos"""
        try:
            if not name:
                messagebox.showwarning("Advertencia", "El nombre del tratamiento es obligatorio")
                return

            if price <= 0:
                messagebox.showwarning("Advertencia", "El precio debe ser mayor que cero")
                return

            if duration <= 0:
                messagebox.showwarning("Advertencia", "La duración debe ser mayor que cero")
                return

            # Llamar al manager para crear el tratamiento
            treatment_id = self.treatment_manager.add_treatment(
                name=name,
                default_price=price,
                description=description,
                duration=duration
            )

            if treatment_id:
                messagebox.showinfo("Éxito", f"Tratamiento creado con ID: {treatment_id}")
                dialog.destroy()
                self.load_treatments()  # Actualizar la lista
            else:
                messagebox.showerror("Error", "No se pudo crear el tratamiento")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el tratamiento: {str(e)}")

    def edit_treatment(self):
        """Muestra diálogo para editar un tratamiento existente"""
        try:
            selected_item = self.treatments_table.selection()
            if not selected_item:
                messagebox.showwarning("Advertencia", "Por favor seleccione un tratamiento")
                return

            item_data = self.treatments_table.item(selected_item)
            treatment_id = item_data['values'][0]

            # Obtener datos completos del tratamiento
            treatment = self.treatment_manager.get_treatment_by_id(treatment_id)
            if not treatment:
                messagebox.showerror("Error", "No se encontró el tratamiento seleccionado")
                return

            # Crear ventana de diálogo
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Editar Tratamiento: {treatment['name']}")
            dialog.transient(self)
            dialog.grab_set()

            # Variables de control
            name_var = ctk.StringVar(value=treatment['name'])
            desc_var = ctk.StringVar(value=treatment['description'])
            price_var = ctk.DoubleVar(value=treatment['default_price'])
            duration_var = ctk.IntVar(value=treatment['duration'])

            # Campos del formulario
            ctk.CTkLabel(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkEntry(dialog, textvariable=name_var, width=300).grid(row=0, column=1, padx=5, pady=5)

            ctk.CTkLabel(dialog, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkEntry(dialog, textvariable=desc_var, width=300).grid(row=1, column=1, padx=5, pady=5)

            ctk.CTkLabel(dialog, text="Precio:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkEntry(dialog, textvariable=price_var, width=100).grid(row=2, column=1, padx=5, pady=5, sticky="w")

            ctk.CTkLabel(dialog, text="Duración (min):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
            ctk.CTkEntry(dialog, textvariable=duration_var, width=100).grid(row=3, column=1, padx=5, pady=5, sticky="w")

            # Botones
            btn_frame = ctk.CTkFrame(dialog)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

            ctk.CTkButton(
                btn_frame,
                text="Guardar",
                command=lambda: self.save_edited_treatment(
                    dialog, treatment_id, name_var.get(), desc_var.get(), price_var.get(), duration_var.get()
                ),
                fg_color="#4CAF50",
                hover_color="#45a049"
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                btn_frame,
                text="Cancelar",
                command=dialog.destroy,
                fg_color="#607D8B",
                hover_color="#546E7A"
            ).pack(side="left", padx=5)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo editar el tratamiento: {str(e)}")

    def save_edited_treatment(self, dialog, treatment_id, name, description, price, duration):
        """Guarda los cambios de un tratamiento editado"""
        try:
            if not name:
                messagebox.showwarning("Advertencia", "El nombre del tratamiento es obligatorio")
                return

            if price <= 0:
                messagebox.showwarning("Advertencia", "El precio debe ser mayor que cero")
                return

            if duration <= 0:
                messagebox.showwarning("Advertencia", "La duración debe ser mayor que cero")
                return

            # Llamar al manager para actualizar el tratamiento
            success = self.treatment_manager.update_treatment(
                treatment_id=treatment_id,
                name=name,
                description=description,
                default_price=price,
                duration=duration
            )

            if success:
                messagebox.showinfo("Éxito", "Tratamiento actualizado correctamente")
                dialog.destroy()
                self.load_treatments()  # Actualizar la lista
            else:
                messagebox.showerror("Error", "No se pudo actualizar el tratamiento")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar los cambios: {str(e)}")

    def delete_treatment(self):
        """Elimina el tratamiento seleccionado"""
        try:
            selected_item = self.treatments_table.selection()
            if not selected_item:
                messagebox.showwarning("Advertencia", "Por favor seleccione un tratamiento")
                return

            item_data = self.treatments_table.item(selected_item)
            treatment_id = item_data['values'][0]
            treatment_name = item_data['values'][1]

            # Confirmar eliminación
            if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el tratamiento '{treatment_name}'?"):
                return

            # Llamar al manager para eliminar (en realidad desactivar)
            success = self.treatment_manager.update_treatment(
                treatment_id=treatment_id,
                active=False
            )

            if success:
                messagebox.showinfo("Éxito", "Tratamiento eliminado correctamente")
                self.load_treatments()  # Actualizar la lista
            else:
                messagebox.showerror("Error", "No se pudo eliminar el tratamiento")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el tratamiento: {str(e)}")

    def search_treatments(self):
        """Busca tratamientos según el criterio ingresado"""
        search_text = self.search_entry.get().strip()
        if not search_text:
            self.load_treatments()
            return

        try:
            # Obtener todos los tratamientos y filtrar localmente
            treatments = self.treatment_manager.get_all_treatments(active_only=False)
            filtered = [
                t for t in treatments
                if (search_text.lower() in t['name'].lower() or
                    search_text.lower() in t.get('description', '').lower() or
                    search_text in str(t['id']))
            ]

            self.treatments_table.delete(*self.treatments_table.get_children())

            for treatment in filtered:
                self.treatments_table.insert("", "end", values=(
                    treatment['id'],
                    treatment['name'],
                    treatment['description'],
                    f"${treatment['default_price']:.2f}",
                    f"{treatment['duration']} min",
                    treatment.get('category_name', 'Sin categoría')
                ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la búsqueda: {str(e)}")

    def update_treatment_info(self, event=None):
        """Actualiza la información mostrada del tratamiento seleccionado"""
        try:
            selected = self.treatment_combo.get()
            if not selected:
                return

            treatment_id = int(selected.split(" - ")[0])
            treatment = self.treatment_manager.get_treatment_by_id(treatment_id)

            if treatment:
                self.price_label.configure(text=f"${treatment['default_price']:.2f}")
                self.duration_label.configure(text=f"{treatment['duration']} minutos")
                self.current_treatment_id = treatment_id

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la información del tratamiento: {str(e)}")

    def assign_treatment(self):
        """Asigna el tratamiento seleccionado al paciente seleccionado"""
        try:
            if not self.current_patient_id:
                messagebox.showwarning("Advertencia", "Por favor seleccione un paciente")
                return

            if not self.current_treatment_id:
                messagebox.showwarning("Advertencia", "Por favor seleccione un tratamiento")
                return

            # Obtener precio personalizado si se especificó
            custom_price = None
            price_text = self.custom_price_entry.get().strip()
            if price_text:
                try:
                    custom_price = float(price_text)
                    if custom_price <= 0:
                        messagebox.showwarning("Advertencia", "El precio debe ser mayor que cero")
                        return
                except ValueError:
                    messagebox.showwarning("Advertencia", "El precio debe ser un número válido")
                    return

            # Obtener notas
            notes = self.notes_entry.get("1.0", "end").strip() or None

            # Aquí necesitaríamos el ID de la cita, pero como no está en el contexto,
            # vamos a simular que creamos una cita primero
            # En una implementación real, esto debería venir de seleccionar una cita existente

            # Simular creación de cita (esto es solo para el ejemplo)
            # En una implementación real, usarías el módulo de citas
            appointment_data = {
                'patient_id': self.current_patient_id,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'status': 'scheduled'
            }

            # Esto debería hacerse con un AppointmentManager
            # appointment_id = self.appointment_manager.create_appointment(appointment_data)

            # Para el ejemplo, usaremos un ID fijo
            appointment_id = 1

            # Asignar tratamiento a la cita
            assignment_id = self.treatment_manager.assign_treatment_to_appointment(
                appointment_id=appointment_id,
                treatment_id=self.current_treatment_id,
                price=custom_price,
                notes=notes
            )

            if assignment_id:
                messagebox.showinfo("Éxito", f"Tratamiento asignado correctamente (ID: {assignment_id})")

                # Limpiar campos
                self.custom_price_entry.delete(0, "end")
                self.notes_entry.delete("1.0", "end")

                # Actualizar historial
                self.filter_history()

                # Opcional: enviar email de confirmación
                # self.send_treatment_email()
            else:
                messagebox.showerror("Error", "No se pudo asignar el tratamiento")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo asignar el tratamiento: {str(e)}")

    def filter_history(self):
        """Filtra el historial según los criterios seleccionados"""
        try:
            # Obtener paciente seleccionado
            patient_text = self.history_patient_combo.get()
            patient_id = int(patient_text.split(" - ")[0]) if patient_text else None

            # Obtener fechas
            date_from = self.date_from_entry.get().strip()
            date_to = self.date_to_entry.get().strip()

            # Convertir fechas al formato YYYY-MM-DD
            try:
                date_from = datetime.strptime(date_from, "%d/%m/%Y").strftime("%Y-%m-%d") if date_from else None
                date_to = datetime.strptime(date_to, "%d/%m/%Y").strftime("%Y-%m-%d") if date_to else None
            except ValueError:
                messagebox.showwarning("Advertencia", "Formato de fecha inválido. Use DD/MM/AAAA")
                return

            # Obtener historial filtrado
            treatments = self.treatment_manager.get_treatments_by_patient(
                patient_id=patient_id
            ) if patient_id else []

            # Filtrar por fecha si es necesario
            if date_from or date_to:
                filtered = []
                for t in treatments:
                    try:
                        treatment_date = datetime.strptime(t['date'], "%Y-%m-%d")

                        if date_from and treatment_date < datetime.strptime(date_from, "%Y-%m-%d"):
                            continue

                        if date_to and treatment_date > datetime.strptime(date_to, "%Y-%m-%d"):
                            continue

                        filtered.append(t)
                    except:
                        continue
                treatments = filtered

            # Mostrar en la tabla
            self.history_table.delete(*self.history_table.get_children())

            for treatment in treatments:
                self.history_table.insert("", "end", values=(
                    treatment['id'],
                    treatment['date'],
                    f"{self.get_patient_name(treatment.get('patient_id', ''))}",
                    treatment.get('treatment_name', ''),
                    f"${treatment.get('price_applied', 0):.2f}",
                    treatment.get('status', '')
                ))

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo filtrar el historial: {str(e)}")

    def get_patient_name(self, patient_id):
        """Obtiene el nombre completo de un paciente por su ID"""
        if not patient_id:
            return "Desconocido"

        patient = self.patient_manager.get_patient_by_id(patient_id)
        if patient:
            return f"{patient.get('nombre', '')} {patient.get('apellidos', '')}"
        return "Desconocido"

    def send_treatment_email(self):
        """Envía por email la información del tratamiento asignado"""
        try:
            if not self.current_patient_id:
                messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
                return

            patient = self.patient_manager.get_patient_by_id(self.current_patient_id)
            if not patient or not patient.get('email'):
                messagebox.showwarning("Advertencia", "El paciente no tiene email registrado")
                return

            # Obtener información del tratamiento asignado
            selected = self.treatment_combo.get()
            if not selected:
                messagebox.showwarning("Advertencia", "No hay tratamiento seleccionado")
                return

            treatment_id = int(selected.split(" - ")[0])
            treatment = self.treatment_manager.get_treatment_by_id(treatment_id)

            if not treatment:
                messagebox.showerror("Error", "No se encontró el tratamiento")
                return

            # Construir mensaje
            subject = f"Confirmación de tratamiento: {treatment['name']}"
            message = f"""
            Estimado/a {patient['nombre']} {patient['apellidos']},

            Se le ha asignado el siguiente tratamiento:

            Nombre: {treatment['name']}
            Descripción: {treatment.get('description', 'No disponible')}
            Precio: ${treatment['default_price']:.2f}
            Duración: {treatment['duration']} minutos

            Por favor, confirme su asistencia respondiendo a este correo.

            Atentamente,
            Su Clínica Dental
            """

            # Enviar email
            # success = send_treatment_email(
            #     to_email=patient['email'],
            #     subject=subject,
            #     body=message
            # )

            # if success:
            #     messagebox.showinfo("Éxito", "Email enviado correctamente")
            # else:
            #     messagebox.showerror("Error", "No se pudo enviar el email")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el email: {str(e)}")
