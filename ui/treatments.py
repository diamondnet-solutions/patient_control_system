# =============================================
# HEADER INFORMATION
# =============================================
# Nombre del archivo: treatments.py
# Propósito: Gestión integral de tratamientos médicos (creación, modificación, asignación)
# Empresa: DiamondNetSolutions
# Autor: Eliazar
# Fecha de creación: 01/05/2025
# =============================================

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional, Dict, Any, List
import os

# Importaciones de módulos internos
from core.treatment_manager import TreatmentManager
from core.patient_manager import PatientManager
from db.database import DatabaseManager  # Añadido para inicializar los managers


class TreatmentsFrame(ttk.Frame):
    """Frame principal para la gestión de tratamientos médicos"""

    def __init__(self, parent):
        """
        Inicializa el frame de tratamientos

        Args:
            parent: Widget padre contenedor de este frame
        """
        super().__init__(parent)
        self.parent = parent

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

        self.pack(fill=tk.BOTH, expand=True)

    def setup_ui(self):
        """Configura la interfaz de usuario principal"""
        # Frame principal con pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pestaña 1: Catálogo de tratamientos
        self.treatments_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.treatments_tab, text="Catálogo")
        self.setup_treatments_tab()

        # Pestaña 2: Asignación de tratamientos
        self.assignment_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.assignment_tab, text="Asignación")
        self.setup_assignment_tab()

        # Pestaña 3: Historial de tratamientos
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="Historial")
        self.setup_history_tab()

    def setup_treatments_tab(self):
        """Configura la pestaña de catálogo de tratamientos"""
        # Frame para botones de acción
        actions_frame = ttk.Frame(self.treatments_tab)
        actions_frame.pack(fill=tk.X, padx=5, pady=5)

        # Botones de acción
        ttk.Button(actions_frame, text="Agregar", command=self.add_treatment).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Editar", command=self.edit_treatment).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Eliminar", command=self.delete_treatment).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Actualizar", command=self.load_treatments).pack(side=tk.LEFT, padx=5)

        # Frame para búsqueda
        search_frame = ttk.Frame(self.treatments_tab)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Buscar", command=self.search_treatments).pack(side=tk.LEFT, padx=5)

        # Tabla de tratamientos
        table_frame = ttk.Frame(self.treatments_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("id", "nombre", "descripción", "precio", "duración", "categoría")
        self.treatments_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configurar columnas
        for col in columns:
            self.treatments_table.heading(col, text=col.capitalize())
            self.treatments_table.column(col, width=120, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.treatments_table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.treatments_table.configure(yscrollcommand=scrollbar.set)

        self.treatments_table.pack(fill=tk.BOTH, expand=True)
        self.treatments_table.bind("<Double-1>", lambda e: self.edit_treatment())

    def setup_assignment_tab(self):
        """Configura la pestaña de asignación de tratamientos"""
        # Frame para selección de paciente
        patient_frame = ttk.LabelFrame(self.assignment_tab, text="Seleccionar Paciente")
        patient_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(patient_frame, text="Paciente:").pack(side=tk.LEFT, padx=5)
        self.patient_combo = ttk.Combobox(patient_frame, state="readonly")
        self.patient_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.patient_combo.bind("<<ComboboxSelected>>", self.on_patient_selected)

        # Frame para selección de tratamiento
        treatment_frame = ttk.LabelFrame(self.assignment_tab, text="Seleccionar Tratamiento")
        treatment_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(treatment_frame, text="Tratamiento:").pack(side=tk.LEFT, padx=5)
        self.treatment_combo = ttk.Combobox(treatment_frame, state="readonly")
        self.treatment_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.treatment_combo.bind("<<ComboboxSelected>>", self.update_treatment_info)

        # Frame para información del tratamiento
        info_frame = ttk.LabelFrame(self.assignment_tab, text="Información del Tratamiento")
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(info_frame, text="Precio:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.price_label = ttk.Label(info_frame, text="$0.00")
        self.price_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

        ttk.Label(info_frame, text="Duración:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.duration_label = ttk.Label(info_frame, text="0 minutos")
        self.duration_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

        # Campo para precio personalizado
        ttk.Label(info_frame, text="Precio personalizado:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.custom_price_entry = ttk.Entry(info_frame)
        self.custom_price_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)

        # Campo para notas
        ttk.Label(info_frame, text="Notas:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.notes_entry = ttk.Entry(info_frame)
        self.notes_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2, columnspan=2)

        # Botón para asignar tratamiento
        ttk.Button(
            self.assignment_tab,
            text="Asignar Tratamiento",
            command=self.assign_treatment
        ).pack(pady=10)

    def setup_history_tab(self):
        """Configura la pestaña de historial de tratamientos"""
        # Frame para filtros
        filter_frame = ttk.Frame(self.history_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(filter_frame, text="Paciente:").pack(side=tk.LEFT, padx=5)
        self.history_patient_combo = ttk.Combobox(filter_frame, state="readonly")
        self.history_patient_combo.pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Fecha desde:").pack(side=tk.LEFT, padx=5)
        self.date_from_entry = ttk.Entry(filter_frame, width=10)
        self.date_from_entry.pack(side=tk.LEFT, padx=5)
        self.date_from_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ttk.Label(filter_frame, text="Fecha hasta:").pack(side=tk.LEFT, padx=5)
        self.date_to_entry = ttk.Entry(filter_frame, width=10)
        self.date_to_entry.pack(side=tk.LEFT, padx=5)
        self.date_to_entry.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ttk.Button(filter_frame, text="Filtrar", command=self.filter_history).pack(side=tk.LEFT, padx=5)

        # Tabla de historial
        table_frame = ttk.Frame(self.history_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        columns = ("id", "fecha", "paciente", "tratamiento", "precio", "estado")
        self.history_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        # Configurar columnas
        for col in columns:
            self.history_table.heading(col, text=col.capitalize())
            self.history_table.column(col, width=120, anchor=tk.CENTER)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.history_table.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_table.configure(yscrollcommand=scrollbar.set)

        self.history_table.pack(fill=tk.BOTH, expand=True)

    # ==================================================================
    # MÉTODOS DE FUNCIONALIDAD
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
            self.treatment_combo['values'] = treatment_list

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los tratamientos: {str(e)}")

    def load_patients_combo(self):
        """Carga la lista de pacientes en los combobox correspondientes"""
        try:
            patients = self.patient_manager.get_all_patients()
            patient_list = [f"{p['id']} - {p['nombre']} {p['apellidos']}" for p in patients]

            self.patient_combo['values'] = patient_list
            self.history_patient_combo['values'] = patient_list

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
            dialog = tk.Toplevel(self)
            dialog.title("Agregar Nuevo Tratamiento")
            dialog.transient(self)  # Hace que la ventana sea modal respecto a la principal
            dialog.grab_set()  # Impide interactuar con otras ventanas

            # Variables de control
            name_var = tk.StringVar()
            desc_var = tk.StringVar()
            price_var = tk.DoubleVar(value=0.0)
            duration_var = tk.IntVar(value=30)

            # Campos del formulario
            ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=desc_var, width=30).grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Precio:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=price_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

            ttk.Label(dialog, text="Duración (min):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=duration_var, width=10).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

            # Botones
            btn_frame = ttk.Frame(dialog)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

            ttk.Button(btn_frame, text="Guardar", command=lambda: self.save_new_treatment(
                dialog, name_var.get(), desc_var.get(), price_var.get(), duration_var.get()
            )).pack(side=tk.LEFT, padx=5)

            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

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
            dialog = tk.Toplevel(self)
            dialog.title(f"Editar Tratamiento: {treatment['name']}")
            dialog.transient(self)
            dialog.grab_set()

            # Variables de control
            name_var = tk.StringVar(value=treatment['name'])
            desc_var = tk.StringVar(value=treatment['description'])
            price_var = tk.DoubleVar(value=treatment['default_price'])
            duration_var = tk.IntVar(value=treatment['duration'])

            # Campos del formulario
            ttk.Label(dialog, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=desc_var, width=30).grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(dialog, text="Precio:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=price_var, width=10).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

            ttk.Label(dialog, text="Duración (min):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
            ttk.Entry(dialog, textvariable=duration_var, width=10).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

            # Botones
            btn_frame = ttk.Frame(dialog)
            btn_frame.grid(row=4, column=0, columnspan=2, pady=10)

            ttk.Button(btn_frame, text="Guardar", command=lambda: self.save_edited_treatment(
                dialog, treatment_id, name_var.get(), desc_var.get(), price_var.get(), duration_var.get()
            )).pack(side=tk.LEFT, padx=5)

            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

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
                self.price_label.config(text=f"${treatment['default_price']:.2f}")
                self.duration_label.config(text=f"{treatment['duration']} minutos")
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
            notes = self.notes_entry.get().strip() or None

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
                self.custom_price_entry.delete(0, tk.END)
                self.notes_entry.delete(0, tk.END)

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