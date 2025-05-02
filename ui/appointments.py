# =============================================
# Nombre del archivo: appointment.py
# Propósito: Gestión integral de citas médicas (creación, modificación, cancelación)
# Empresa: DiamondNetSolutions
# Autor: Eliazar
# Fecha de creación: 30/04/2025
# =============================================

import tkinter as tk
from tkinter import ttk, messagebox
import re

from datetime import datetime
from typing import Optional, Dict, Any
from tkcalendar import Calendar, DateEntry

from core.appointment_manager import AppointmentManager
from core.patient_manager import PatientManager
from core.treatment_manager import TreatmentManager
from utils.email_handler import send_appointment_email


class AppointmentsFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.appointments_table = None
        self.email_button = None
        self.edit_button = None
        self.table_frame = None
        self.patient_combo = None
        self.action_frame = None
        self.new_button = None
        self.complete_button = None
        self.cancel_button = None
        self.status_var = None
        self.patient_var = None
        self.search_button = None
        self.status_combo = None
        self.date_entry = None
        self.filter_frame = None
        self.calendar = None
        self.calendar_frame = None
        self.top_frame = None
        self.pack(fill=tk.BOTH, expand=True)

        # Inicializar managers
        self.appointment_manager = AppointmentManager()
        self.patient_manager = PatientManager()
        self.treatment_manager = TreatmentManager()

        # Configurar interfaz
        self.setup_ui()

        # Cargar datos iniciales
        self.load_appointments()

    def setup_ui(self):
        """Configura la interfaz de usuario para la gestión de citas"""
        # Marco superior con calendario y filtros
        self.top_frame = ttk.Frame(self)
        self.top_frame.pack(fill=tk.X, pady=10)

        # Parte izquierda: Calendario
        self.calendar_frame = ttk.LabelFrame(self.top_frame, text="Calendario")
        self.calendar_frame.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.calendar = Calendar(self.calendar_frame, selectmode='day',
                                 locale='es_ES',
                                 date_pattern='dd/mm/yyyy')
        self.calendar.pack(padx=10, pady=10)
        self.calendar.bind("<<CalendarSelected>>", self.on_date_selected)

        # Parte derecha: Filtros y controles
        self.filter_frame = ttk.LabelFrame(self.top_frame, text="Filtros")
        self.filter_frame.pack(side=tk.RIGHT, padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Control de fecha
        ttk.Label(self.filter_frame, text="Fecha:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.date_entry = DateEntry(self.filter_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.date_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.date_entry.bind("<<DateEntrySelected>>", self.on_date_entry_selected)

        # Filtro por paciente
        ttk.Label(self.filter_frame, text="Paciente:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.patient_var = tk.StringVar()
        self.patient_combo = ttk.Combobox(self.filter_frame, textvariable=self.patient_var, width=20)
        self.patient_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.load_patients_combo()

        # Filtro por estado
        ttk.Label(self.filter_frame, text="Estado:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.status_var = tk.StringVar(value="Todos")
        self.status_combo = ttk.Combobox(self.filter_frame, textvariable=self.status_var, width=20)
        self.status_combo['values'] = ("Todos", "Programada", "Confirmada", "Completada", "Cancelada")
        self.status_combo.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Botón de búsqueda
        self.search_button = ttk.Button(self.filter_frame, text="Buscar", command=self.search_appointments)
        self.search_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Marco para botones de acción
        self.action_frame = ttk.Frame(self)
        self.action_frame.pack(fill=tk.X, pady=5)

        # Botones de acción
        self.new_button = ttk.Button(self.action_frame, text="Nueva Cita", command=self.new_appointment)
        self.new_button.pack(side=tk.LEFT, padx=5)

        self.edit_button = ttk.Button(self.action_frame, text="Editar Cita", command=self.edit_appointment)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = ttk.Button(self.action_frame, text="Cancelar Cita", command=self.cancel_appointment)
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        self.complete_button = ttk.Button(self.action_frame, text="Completar Cita", command=self.complete_appointment)
        self.complete_button.pack(side=tk.LEFT, padx=5)

        self.email_button = ttk.Button(self.action_frame, text="Enviar Recordatorio", command=self.send_reminder)
        self.email_button.pack(side=tk.LEFT, padx=5)

        # Marco para la tabla de citas
        self.table_frame = ttk.LabelFrame(self, text="Citas")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tabla de citas
        self.setup_appointments_table()

    def setup_appointments_table(self):
        """Configura la tabla de citas"""
        columns = ("id", "patient", "date", "time", "status", "notes")
        self.appointments_table = ttk.Treeview(self.table_frame, columns=columns, show='headings')

        # Definir encabezados
        self.appointments_table.heading("id", text="ID")
        self.appointments_table.heading("patient", text="Paciente")
        self.appointments_table.heading("date", text="Fecha")
        self.appointments_table.heading("time", text="Hora")
        self.appointments_table.heading("status", text="Estado")
        self.appointments_table.heading("notes", text="Notas")

        # Configurar columnas
        self.appointments_table.column("id", width=50)
        self.appointments_table.column("patient", width=200)
        self.appointments_table.column("date", width=100)
        self.appointments_table.column("time", width=100)
        self.appointments_table.column("status", width=100)
        self.appointments_table.column("notes", width=200)

        # Añadir scrollbars
        scrollbar_y = ttk.Scrollbar(self.table_frame, orient=tk.VERTICAL, command=self.appointments_table.yview)
        self.appointments_table.configure(yscroll=scrollbar_y.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        scrollbar_x = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL, command=self.appointments_table.xview)
        self.appointments_table.configure(xscroll=scrollbar_x.set)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.appointments_table.pack(fill=tk.BOTH, expand=True)


        # Vincular evento de doble clic
        self.appointments_table.bind("<Double-1>", self.on_double_click_edit)

    def on_double_click_edit(self):
        self.edit_appointment()

    def load_patients_combo(self):
        """Carga la lista de pacientes en el combobox"""
        patients = self.patient_manager.get_all_patients()
        print(patients)  # Debug
        patient_values = ["Todos"] + [f"{p['nombre']} {p['apellidos']} (ID: {p['id']})" for p in patients]
        self.patient_combo['values'] = patient_values
        self.patient_var.set("Todos")

    def load_appointments(self, date=None, patient_id=None, status=None):
        """Carga las citas según los filtros aplicados"""
        # Limpiar tabla
        for item in self.appointments_table.get_children():
            self.appointments_table.delete(item)

        # Obtener citas filtradas
        appointments = self.appointment_manager.get_filtered_appointments(date, patient_id, status)

        # Cargar citas en la tabla
        for appointment in appointments:
            patient_name = f"{appointment['patient_first_name']} {appointment['patient_last_name']}"
            time_str = f"{appointment['start_time']} - {appointment['end_time']}"

            # Status en español
            status_map = {
                "scheduled": "Programada",
                "confirmed": "Confirmada",
                "completed": "Completada",
                "cancelled": "Cancelada"
            }
            status_text = status_map.get(appointment['status'], appointment['status'])

            self.appointments_table.insert("", tk.END, values=(
                appointment['id'],
                patient_name,
                appointment['date'],
                time_str,
                status_text,
                appointment['notes'] if appointment['notes'] else ""
            ))

    def on_date_selected(self):
        """Maneja la selección de fecha en el calendario"""
        selected_date = self.calendar.get_date()
        self.date_entry.set_date(datetime.datetime.strptime(selected_date, "%d/%m/%Y"))
        self.search_appointments()

    def on_date_entry_selected(self):
        """Maneja la selección de fecha en el entry"""
        selected_date = self.date_entry.get_date()
        self.calendar.selection_set(selected_date)
        self.search_appointments()

    def search_appointments(self):
        """Busca citas según los filtros aplicados"""
        # Obtener fecha seleccionada
        date_str = self.date_entry.get_date().strftime("%Y-%m-%d") if self.date_entry.get_date() else None

        # Obtener paciente seleccionado
        patient_id = None
        if self.patient_var.get() != "Todos":
            # Extraer ID del paciente del texto del combo
            match = re.search(r'ID: (\d+)', self.patient_var.get())
            if match:
                patient_id = int(match.group(1))

        # Obtener estado seleccionado
        status = None
        if self.status_var.get() != "Todos":
            # Mapear estado en español a inglés
            status_map = {
                "Programada": "scheduled",
                "Confirmada": "confirmed",
                "Completada": "completed",
                "Cancelada": "cancelled"
            }
            status = status_map.get(self.status_var.get())

        # Cargar citas filtradas
        self.load_appointments(date_str, patient_id, status)

    def new_appointment(self):
        """Abre el diálogo para crear una nueva cita"""
        AppointmentDialog(self, "nueva")

    def edit_appointment(self):
        """Edita la cita seleccionada"""
        selected_item = self.appointments_table.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione una cita para editar.")
            return

        appointment_id = self.appointments_table.item(selected_item[0], "values")[0]
        AppointmentDialog(self, "editar", appointment_id)

    def cancel_appointment(self):
        """Cancela la cita seleccionada"""
        selected_item = self.appointments_table.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione una cita para cancelar.")
            return

        # Obtener datos de la cita seleccionada
        appointment_data = self.appointments_table.item(selected_item[0], "values")
        appointment_id = appointment_data[0]
        patient_name = appointment_data[1]

        # Confirmar cancelación
        confirm = messagebox.askyesno(
            "Confirmar Cancelación",
            f"¿Está seguro que desea cancelar la cita de {patient_name} (ID: {appointment_id})?"
        )

        if confirm:
            try:
                # Actualizar estado en la base de datos
                success = self.appointment_manager.update_appointment_status(
                    appointment_id,
                    "cancelled"
                )

                if success:
                    messagebox.showinfo(
                        "Éxito",
                        f"Cita {appointment_id} cancelada correctamente."
                    )
                    # Actualizar tabla
                    self.search_appointments()
                else:
                    messagebox.showerror(
                        "Error",
                        "No se pudo cancelar la cita. Intente nuevamente."
                    )
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Ocurrió un error al cancelar la cita: {str(e)}"
                )


    def complete_appointment(self):
        """Marca la cita seleccionada como completada"""
        selected_item = self.appointments_table.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione una cita para marcar como completada.")
            return

        appointment_id = self.appointments_table.item(selected_item[0], "values")[0]

        try:
            success = self.appointment_manager.update_appointment_status(
                appointment_id,
                "completed"
            )

            if success:
                messagebox.showinfo("Éxito", "Cita marcada como completada.")
                self.search_appointments()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la cita.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al completar cita: {str(e)}")

    def send_reminder(self):
        """Envía un recordatorio por email para la cita seleccionada"""
        selected_item = self.appointments_table.selection()
        if not selected_item:
            messagebox.showwarning("Selección", "Por favor, seleccione una cita para enviar recordatorio.")
            return

        appointment_data = self.appointments_table.item(selected_item[0], "values")
        appointment_id = appointment_data[0]

        try:
            # Obtener datos completos de la cita
            appointment = self.appointment_manager.get_appointment_by_id(appointment_id)
            patient = self.patient_manager.get_patient_by_id(appointment['patient_id'])

            # Construir mensaje
            subject = f"Recordatorio de cita - {appointment['date']} {appointment['start_time']}"
            body = f"""
            Estimado/a {patient['first_name']} {patient['last_name']},

            Le recordamos su cita programada para:

            Fecha: {appointment['date']}
            Hora: {appointment['start_time']} - {appointment['end_time']}

            Notas: {appointment.get('notes', 'Ninguna')}

            Por favor confirme su asistencia.
            """

            # Enviar email
            send_appointment_email(patient['email'], subject, body)
            messagebox.showinfo("Éxito", "Recordatorio enviado correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo enviar el recordatorio: {str(e)}")

class AppointmentDialog(tk.Toplevel):
    def __init__(self, parent, mode: str, appointment_id: Optional[int] = None):
        super().__init__(parent)
        self.parent = parent
        self.mode = mode
        self.appointment_id = appointment_id
        self.patient_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.start_time_var = tk.StringVar()
        self.end_time_var = tk.StringVar()
        self.notes_var = tk.StringVar()

        self.title("Nueva Cita" if mode == "nueva" else "Editar Cita")
        self.geometry("500x400")
        self.resizable(False, False)
        self.setup_ui()

        if mode == "editar":
            self.load_appointment_data()

    def setup_ui(self):
        """Configura los elementos de la interfaz"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Paciente
        ttk.Label(main_frame, text="Paciente:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.patient_combo = ttk.Combobox(main_frame, textvariable=self.patient_var, width=30)
        self.patient_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.load_patients()

        # Fecha
        ttk.Label(main_frame, text="Fecha:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.date_entry = DateEntry(main_frame, textvariable=self.date_var, width=12,
                                  date_pattern='dd/mm/yyyy')
        self.date_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Hora de inicio
        ttk.Label(main_frame, text="Hora Inicio (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.start_time_combo = ttk.Combobox(main_frame, textvariable=self.start_time_var, width=8)
        self.start_time_combo['values'] = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in (0, 15, 30, 45)]
        self.start_time_combo.grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="Formato: 08:00 - 19:45").grid(row=2, column=2, sticky=tk.W, padx=5)

        # Hora de fin
        ttk.Label(main_frame, text="Hora Fin (HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.end_time_combo = ttk.Combobox(main_frame, textvariable=self.end_time_var, width=8)
        self.end_time_combo['values'] = [f"{h:02d}:{m:02d}" for h in range(8, 20) for m in (0, 15, 30, 45)]
        self.end_time_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        ttk.Label(main_frame, text="Formato: 08:15 - 20:00").grid(row=3, column=2, sticky=tk.W, padx=5)

        # Notas
        ttk.Label(main_frame, text="Notas:").grid(row=4, column=0, sticky=tk.NW, pady=5)
        self.notes_text = tk.Text(main_frame, width=30, height=5)
        self.notes_text.grid(row=4, column=1, sticky=tk.W, pady=5)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Guardar", command=self.save_appointment).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def load_patients(self):
        """Carga la lista de pacientes en el combobox"""
        patients = self.parent.patient_manager.get_all_patients()
        self.patient_combo['values'] = [f"{p['nombre']} {p['apellidos']} (ID: {p['id']})" for p in patients]

    def load_appointment_data(self):
        """Carga los datos de la cita existente"""
        if not self.appointment_id:
            return

        appointment = self.parent.appointment_manager.get_appointment_by_id(self.appointment_id)
        if not appointment:
            messagebox.showerror("Error", "No se pudo cargar la cita.")
            self.destroy()
            return

        patient = self.parent.patient_manager.get_patient_by_id(appointment['patient_id'])
        self.patient_var.set(f"{patient['nombre']} {patient['apellidos']} (ID: {patient['id']})")
        self.date_var.set(appointment['date'])
        self.start_time_var.set(appointment['start_time'])
        self.end_time_var.set(appointment['end_time'])
        self.notes_text.insert("1.0", appointment.get('notes', ''))

    def save_appointment(self):
        """Guarda los cambios de la cita"""
        try:
            # Validar datos
            if not self.patient_var.get():
                messagebox.showerror("Error", "Seleccione un paciente.")
                return

            # Extraer ID del paciente
            match = re.search(r'ID: (\d+)', self.patient_var.get())
            if not match:
                messagebox.showerror("Error", "Formato de paciente inválido.")
                return
            patient_id = int(match.group(1))

            date = self.date_entry.get_date().strftime("%Y-%m-%d")
            start_time = self.start_time_var.get()
            end_time = self.end_time_var.get()
            notes = self.notes_text.get("1.0", tk.END).strip()

            # Verificar disponibilidad (solo para citas nuevas)
            if self.mode == "nueva":
                if not self.parent.appointment_manager.is_time_available(date, start_time, end_time):
                    messagebox.showerror("Error", "El horario seleccionado no está disponible.")
                    return

            # Crear/actualizar cita
            appointment_data = {
                'patient_id': patient_id,
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'notes': notes
            }

            if self.mode == "nueva":
                appointment_id = self.parent.appointment_manager.create_appointment(
                    patient_id, date, start_time, end_time, "", notes
                )
                if appointment_id:
                    messagebox.showinfo("Éxito", "Cita creada correctamente.")
            else:
                success = self.parent.appointment_manager.update_appointment(
                    self.appointment_id,
                    appointment_data
                )
                if success:
                    messagebox.showinfo("Éxito", "Cita actualizada correctamente.")

            self.parent.search_appointments()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la cita: {str(e)}")